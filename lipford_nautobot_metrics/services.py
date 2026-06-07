"""Metric collection and population services."""

from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Count, Max
from django.utils import timezone

from lipford_nautobot_metrics.catalog import METRIC_CATALOG
from lipford_nautobot_metrics.choices import MetricKindChoices, MetricUnitChoices
from lipford_nautobot_metrics.models import MetricDefinition, MetricValue

SAMPLE_SOURCE = "lipford_nautobot_metrics.full_catalog_sample_job"
DEFAULT_SAMPLE_DAYS = 3
MAX_SAMPLE_DAYS = 30

DEFAULT_TARGETS = {
    MetricKindChoices.TIME_SAVED_PER_AUTOMATED_TASK: Decimal("1.7500"),
    MetricKindChoices.MANUAL_ERROR_RATE_REDUCTION: Decimal("90.0000"),
    MetricKindChoices.INCREASED_TASK_THROUGHPUT: Decimal("400.0000"),
    MetricKindChoices.AUTOMATION_ADOPTION_RATE: Decimal("60.0000"),
}

DEFAULT_METRIC_DEFINITIONS: tuple[dict[str, Any], ...] = tuple(
    {
        **{key: value for key, value in definition.items() if key != "bounded"},
        "baseline_value": Decimal("0.0000"),
        "target_value": DEFAULT_TARGETS.get(definition["key"]),
    }
    for definition in METRIC_CATALOG
)


def get_app_settings() -> dict[str, Any]:
    """Return app settings with defensive defaults for direct test usage."""
    plugin_settings = getattr(settings, "PLUGINS_CONFIG", {}).get("lipford_nautobot_metrics", {})
    return {
        "sample_metric_days": plugin_settings.get("sample_metric_days", DEFAULT_SAMPLE_DAYS),
        "sample_metric_source": plugin_settings.get("sample_metric_source", SAMPLE_SOURCE),
    }


def seed_sample_metrics(sample_days: int | None = None, dryrun: bool = False) -> dict[str, int]:
    """Create or update deterministic sample metrics for early dashboard validation.

    Args:
        sample_days: Number of daily observations to seed for each supported metric.
        dryrun: When true, execute validation and return counts without committing writes.

    Returns:
        Count details for definitions and metric observations.

    Raises:
        ValueError: Raised when ``sample_days`` is outside the supported range.
    """
    if sample_days is None:
        sample_days = get_app_settings()["sample_metric_days"]

    if sample_days < 1 or sample_days > MAX_SAMPLE_DAYS:
        raise ValueError(f"sample_days must be between 1 and {MAX_SAMPLE_DAYS}.")

    result = {
        "definitions_created": 0,
        "definitions_updated": 0,
        "values_created": 0,
        "values_updated": 0,
    }

    with transaction.atomic():
        definitions = _upsert_metric_definitions(result)
        _upsert_sample_values(definitions=definitions, sample_days=sample_days, result=result)

        if dryrun:
            transaction.set_rollback(True)

    return result


def get_metric_summaries() -> list[dict[str, Any]]:
    """Return dashboard-ready summary data for all metric definitions."""
    definitions = (
        MetricDefinition.objects.filter(enabled=True)
        .annotate(
            value_count=Count("values"),
            average_value=Avg("values__value"),
            latest_recorded_at=Max("values__recorded_at"),
        )
        .order_by("name")
    )

    summaries = []
    for definition in definitions:
        latest_value = definition.values.order_by("-recorded_at").first()
        summaries.append(
            {
                "id": definition.pk,
                "name": definition.name,
                "key": definition.key,
                "category": definition.category,
                "kind": definition.kind,
                "unit": definition.unit,
                "target_value": definition.target_value,
                "value_count": definition.value_count,
                "average_value": definition.average_value,
                "latest_recorded_at": definition.latest_recorded_at,
                "latest_value": latest_value.value if latest_value else None,
                "latest_source": latest_value.source if latest_value else "",
            }
        )

    return summaries


def _upsert_metric_definitions(result: dict[str, int]) -> dict[str, MetricDefinition]:
    """Create or update the full-catalog metric definitions."""
    definitions = {}

    for definition_data in DEFAULT_METRIC_DEFINITIONS:
        definition, created = MetricDefinition.objects.get_or_create(
            key=definition_data["key"],
            defaults=definition_data,
        )

        if created:
            result["definitions_created"] += 1
        else:
            changed = _apply_changed_fields(definition, definition_data)
            if changed:
                definition.full_clean()
                definition.save()
                result["definitions_updated"] += 1

        definitions[definition.key] = definition

    return definitions


def _upsert_sample_values(
    definitions: dict[str, MetricDefinition],
    sample_days: int,
    result: dict[str, int],
) -> None:
    """Create or update deterministic sample observations for the full catalog."""
    base_recorded_at = timezone.localtime(timezone.now()).replace(hour=12, minute=0, second=0, microsecond=0)
    start_recorded_at = base_recorded_at - timedelta(days=sample_days - 1)
    source = get_app_settings()["sample_metric_source"]

    for day_index in range(sample_days):
        recorded_at = start_recorded_at + timedelta(days=day_index)

        for metric_index, definition in enumerate(METRIC_CATALOG):
            metric_definition = definitions[definition["key"]]
            _upsert_metric_value(
                metric_definition=metric_definition,
                recorded_at=recorded_at,
                value=_sample_value(metric_definition.unit, metric_index, day_index, definition["bounded"]),
                context={
                    "catalog_category": metric_definition.category,
                    "sample_series": metric_definition.key,
                    "sample_day_index": day_index,
                },
                notes="Deterministic sample observation generated for full-catalog validation.",
                source=source,
                result=result,
            )


def _sample_value(unit: str, metric_index: int, day_index: int, bounded: bool) -> Decimal:
    """Return a deterministic, validation-safe sample value by unit."""
    seed = Decimal(metric_index + day_index + 1)
    if bounded:
        return min(Decimal("40.0000") + seed, Decimal("95.0000"))
    if unit == MetricUnitChoices.PERCENT:
        return Decimal("100.0000") + seed * Decimal("5.0000")
    if unit == MetricUnitChoices.DOLLARS:
        return seed * Decimal("1000.0000")
    if unit == MetricUnitChoices.SECONDS:
        return seed * Decimal("30.0000")
    if unit == MetricUnitChoices.HOURS:
        return seed * Decimal("1.2500")
    if unit == MetricUnitChoices.DAYS:
        return seed * Decimal("0.5000")
    if unit == MetricUnitChoices.BYTES:
        return seed * Decimal("1048576.0000")
    return seed


def _upsert_metric_value(
    metric_definition: MetricDefinition,
    recorded_at,
    value: Decimal,
    context: dict[str, Any],
    notes: str,
    source: str,
    result: dict[str, int],
) -> None:
    """Create or update one metric observation."""
    try:
        metric_value = MetricValue.objects.get(
            metric_definition=metric_definition,
            recorded_at=recorded_at,
            source=source,
        )
        created = False
    except MetricValue.DoesNotExist:
        metric_value = MetricValue(
            metric_definition=metric_definition,
            recorded_at=recorded_at,
            source=source,
        )
        created = True

    changed = _apply_changed_fields(
        metric_value,
        {
            "value": value,
            "context": context,
            "notes": notes,
        },
    )

    if created or changed:
        metric_value.full_clean()
        metric_value.save()

    if created:
        result["values_created"] += 1
    elif changed:
        result["values_updated"] += 1


def _apply_changed_fields(instance, field_values: dict[str, Any]) -> bool:
    """Apply changed field values to a Django model instance."""
    changed = False
    for field_name, value in field_values.items():
        if getattr(instance, field_name) != value:
            setattr(instance, field_name, value)
            changed = True
    return changed
