"""Metric collection and population services."""

from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Count, Max
from django.utils import timezone

from lipford_nautobot_metrics.choices import MetricCategoryChoices, MetricKindChoices, MetricUnitChoices
from lipford_nautobot_metrics.models import MetricDefinition, MetricValue

SAMPLE_SOURCE = "lipford_nautobot_metrics.phase2_sample_job"
DEFAULT_SAMPLE_DAYS = 3
MAX_SAMPLE_DAYS = 30

DEFAULT_METRIC_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "name": "Time Saved per Automated Task",
        "key": MetricKindChoices.TIME_SAVED_PER_AUTOMATED_TASK,
        "category": MetricCategoryChoices.ROI,
        "kind": MetricKindChoices.TIME_SAVED_PER_AUTOMATED_TASK,
        "unit": MetricUnitChoices.HOURS,
        "description": "Reduction in time required to complete a repeatable network task using Nautobot automation.",
        "formula": "Time_Manual - Time_Automated",
        "baseline_value": Decimal("0.0000"),
        "target_value": Decimal("1.7500"),
        "enabled": True,
    },
    {
        "name": "Automation Adoption Rate",
        "key": MetricKindChoices.AUTOMATION_ADOPTION_RATE,
        "category": MetricCategoryChoices.ROI,
        "kind": MetricKindChoices.AUTOMATION_ADOPTION_RATE,
        "unit": MetricUnitChoices.PERCENT,
        "description": "Percentage of target tasks or processes executed through Nautobot automation.",
        "formula": "(Number_of_Tasks_Automated / Total_Potential_Tasks_for_Automation) * 100",
        "baseline_value": Decimal("0.0000"),
        "target_value": Decimal("60.0000"),
        "enabled": True,
    },
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
    """Create or update the Phase 2 metric definitions."""
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
    """Create or update sample observations for the Phase 2 metrics."""
    base_recorded_at = timezone.localtime(timezone.now()).replace(hour=12, minute=0, second=0, microsecond=0)
    start_recorded_at = base_recorded_at - timedelta(days=sample_days - 1)
    source = get_app_settings()["sample_metric_source"]

    for day_index in range(sample_days):
        recorded_at = start_recorded_at + timedelta(days=day_index)

        _upsert_metric_value(
            metric_definition=definitions[MetricKindChoices.TIME_SAVED_PER_AUTOMATED_TASK],
            recorded_at=recorded_at,
            value=Decimal("1.2500") + Decimal("0.2500") * day_index,
            context={
                "task_name": "VLAN provisioning",
                "manual_hours": "2.0000",
                "automated_hours": str(Decimal("0.7500") - Decimal("0.2500") * min(day_index, 2)),
            },
            notes="Sample ROI observation generated for Phase 2 validation.",
            source=source,
            result=result,
        )

        _upsert_metric_value(
            metric_definition=definitions[MetricKindChoices.AUTOMATION_ADOPTION_RATE],
            recorded_at=recorded_at,
            value=min(Decimal("45.0000") + Decimal("5.0000") * day_index, Decimal("95.0000")),
            context={
                "automated_tasks": 30 + day_index * 3,
                "total_target_tasks": 50,
                "team": "network automation",
            },
            notes="Sample adoption observation generated for Phase 2 validation.",
            source=source,
            result=result,
        )


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
