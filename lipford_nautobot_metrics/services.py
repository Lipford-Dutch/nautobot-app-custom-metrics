"""Metric collection and population services."""

from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Count, DecimalField, OuterRef, Subquery
from django.utils import timezone
from nautobot.extras.choices import JobResultStatusChoices, ObjectChangeActionChoices
from nautobot.extras.models import JobResult, ObjectChange

from lipford_nautobot_metrics.catalog import EXPECTED_CATEGORY_COUNTS, EXPECTED_METRIC_COUNT, METRIC_CATALOG
from lipford_nautobot_metrics.choices import MetricKindChoices, MetricUnitChoices
from lipford_nautobot_metrics.models import MetricDefinition, MetricValue

SAMPLE_SOURCE = "lipford_nautobot_metrics.full_catalog_sample_job"
DEFAULT_SAMPLE_DAYS = 3
MAX_SAMPLE_DAYS = 30
DEFAULT_COLLECTOR_LOOKBACK_MINUTES = 60
DEFAULT_MAX_INGEST_BATCH_SIZE = 500
DEFAULT_RETENTION_DAYS = 0
MAX_RETENTION_DAYS = 3650
JOB_RESULT_SOURCE = "lipford_nautobot_metrics.job_result_collector"
OBJECT_CHANGE_SOURCE = "lipford_nautobot_metrics.object_change_collector"
CATALOG_MANAGED_FIELDS = ("name", "category", "kind", "unit", "description", "formula")

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
        "collector_lookback_minutes": plugin_settings.get(
            "collector_lookback_minutes", DEFAULT_COLLECTOR_LOOKBACK_MINUTES
        ),
        "max_ingest_batch_size": plugin_settings.get("max_ingest_batch_size", DEFAULT_MAX_INGEST_BATCH_SIZE),
        "retention_days": plugin_settings.get("retention_days", DEFAULT_RETENTION_DAYS),
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
    latest_values = MetricValue.objects.filter(metric_definition=OuterRef("pk")).order_by("-recorded_at")
    definitions = (
        MetricDefinition.objects.filter(enabled=True)
        .annotate(
            value_count=Count("values"),
            average_value=Avg("values__value"),
            latest_recorded_at=Subquery(latest_values.values("recorded_at")[:1]),
            latest_value=Subquery(latest_values.values("value")[:1], output_field=DecimalField()),
            latest_source=Subquery(latest_values.values("source")[:1]),
        )
        .order_by("name")
    )

    summaries = []
    for definition in definitions:
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
                "latest_value": definition.latest_value,
                "latest_source": definition.latest_source or "",
            }
        )

    return summaries


def get_metric_summary_groups(summaries: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return dashboard-ready metric summaries grouped by canonical category."""
    summaries = summaries if summaries is not None else get_metric_summaries()
    grouped = {
        category: {
            "category": category,
            "label": _category_label(category),
            "expected_count": expected_count,
            "definition_count": 0,
            "value_count": 0,
            "metrics": [],
        }
        for category, expected_count in EXPECTED_CATEGORY_COUNTS.items()
    }

    for summary in summaries:
        group = grouped.setdefault(
            summary["category"],
            {
                "category": summary["category"],
                "label": _category_label(summary["category"]),
                "expected_count": 0,
                "definition_count": 0,
                "value_count": 0,
                "metrics": [],
            },
        )
        group["metrics"].append(summary)
        group["definition_count"] += 1
        group["value_count"] += summary["value_count"]

    return list(grouped.values())


def get_metric_saturation_summary(summaries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Return dashboard saturation status for the canonical catalog."""
    summaries = summaries if summaries is not None else get_metric_summaries()
    enabled_keys = {summary["key"] for summary in summaries}
    catalog_keys = {definition["key"] for definition in METRIC_CATALOG}
    missing_enabled_keys = sorted(catalog_keys - enabled_keys)
    observed_keys = {summary["key"] for summary in summaries if summary["value_count"] > 0}
    missing_observation_keys = sorted(catalog_keys - observed_keys)
    return {
        "expected_count": EXPECTED_METRIC_COUNT,
        "enabled_count": len(enabled_keys),
        "observed_count": len(observed_keys),
        "missing_enabled_keys": missing_enabled_keys,
        "missing_observation_keys": missing_observation_keys,
        "is_fully_enabled": not missing_enabled_keys,
        "is_fully_observed": not missing_observation_keys,
    }


def _category_label(category: str) -> str:
    """Return a compact display label for a metric category."""
    labels = {
        "roi": "ROI",
        "business_impact": "Business Impact",
        "user_activity": "User Activity",
        "plugin_golden_config": "Golden Config",
        "plugin_ssot": "SSoT",
        "plugin_dlm": "DLM",
        "job_execution": "Job Execution",
    }
    return labels.get(category, category.replace("_", " ").title())


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
            changed = _apply_changed_fields(
                definition,
                {field: definition_data[field] for field in CATALOG_MANAGED_FIELDS},
            )
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


# pylint: disable-next=too-many-return-statements  # readable per-unit dispatch
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


def ingest_metric_values(observations: list[dict[str, Any]]) -> dict[str, int]:
    """Atomically validate and upsert externally supplied metric observations."""
    max_batch_size = get_app_settings()["max_ingest_batch_size"]
    if not observations:
        raise ValueError("At least one metric observation is required.")
    if len(observations) > max_batch_size:
        raise ValueError(f"A maximum of {max_batch_size} metric observations is allowed per request.")

    keys = {observation["metric_key"] for observation in observations}
    definitions = MetricDefinition.objects.in_bulk(keys, field_name="key")
    missing = sorted(keys - definitions.keys())
    if missing:
        raise ValueError(f"Unknown metric keys: {', '.join(missing)}.")

    result = {"created": 0, "updated": 0}
    with transaction.atomic():
        for observation in observations:
            counters = {"values_created": 0, "values_updated": 0}
            _upsert_metric_value(
                metric_definition=definitions[observation["metric_key"]],
                recorded_at=observation["recorded_at"],
                value=observation["value"],
                context=observation.get("context", {}),
                notes=observation.get("notes", ""),
                source=observation["source"],
                result=counters,
            )
            result["created"] += counters["values_created"]
            result["updated"] += counters["values_updated"]
    return result


def purge_metric_values(retention_days: int | None = None, dryrun: bool = False) -> dict[str, Any]:
    """Delete observations older than the configured retention window."""
    retention_days = get_app_settings()["retention_days"] if retention_days is None else retention_days
    if retention_days < 1 or retention_days > MAX_RETENTION_DAYS:
        raise ValueError(f"retention_days must be between 1 and {MAX_RETENTION_DAYS}.")
    cutoff = timezone.now() - timedelta(days=retention_days)
    queryset = MetricValue.objects.filter(recorded_at__lt=cutoff)
    result = {"deleted": queryset.count(), "cutoff": cutoff}
    if not dryrun:
        queryset.delete()
    return result


def collect_nautobot_metrics(
    lookback_minutes: int | None = None,
    dryrun: bool = False,
    recorded_at=None,
) -> dict[str, int]:
    """Collect reference metrics from Nautobot JobResult and ObjectChange records."""
    lookback_minutes = lookback_minutes or get_app_settings()["collector_lookback_minutes"]
    if lookback_minutes < 1 or lookback_minutes > 10080:
        raise ValueError("lookback_minutes must be between 1 and 10080.")
    recorded_at = (recorded_at or timezone.now()).replace(second=0, microsecond=0)
    window_start = recorded_at - timedelta(minutes=lookback_minutes)
    definitions = MetricDefinition.objects.in_bulk(
        {
            "job_execution_total_count",
            "job_execution_status_rate",
            "job_execution_duration",
            "object_creation_count",
            "object_update_count",
            "object_deletion_count",
        },
        field_name="key",
    )
    required = {
        "job_execution_total_count",
        "job_execution_status_rate",
        "job_execution_duration",
        "object_creation_count",
        "object_update_count",
        "object_deletion_count",
    }
    missing = sorted(required - definitions.keys())
    if missing:
        raise ValueError(f"Seed metric definitions before collection. Missing: {', '.join(missing)}.")

    completed_jobs = JobResult.objects.filter(date_done__gte=window_start, date_done__lte=recorded_at)
    job_count = completed_jobs.count()
    success_count = completed_jobs.filter(status=JobResultStatusChoices.STATUS_SUCCESS).count()
    durations = [
        (job.date_done - (job.date_started or job.date_created)).total_seconds()
        for job in completed_jobs.only("date_created", "date_started", "date_done")
        if job.date_done
    ]
    observations = [
        ("job_execution_total_count", Decimal(job_count), JOB_RESULT_SOURCE),
        (
            "job_execution_status_rate",
            Decimal(success_count) * Decimal(100) / Decimal(job_count) if job_count else Decimal(0),
            JOB_RESULT_SOURCE,
        ),
        (
            "job_execution_duration",
            Decimal(str(sum(durations) / len(durations))) if durations else Decimal(0),
            JOB_RESULT_SOURCE,
        ),
    ]
    changes = ObjectChange.objects.filter(time__gte=window_start, time__lte=recorded_at)
    for action, key in (
        (ObjectChangeActionChoices.ACTION_CREATE, "object_creation_count"),
        (ObjectChangeActionChoices.ACTION_UPDATE, "object_update_count"),
        (ObjectChangeActionChoices.ACTION_DELETE, "object_deletion_count"),
    ):
        observations.append((key, Decimal(changes.filter(action=action).count()), OBJECT_CHANGE_SOURCE))

    result = {"created": 0, "updated": 0}
    with transaction.atomic():
        for key, value, source in observations:
            counters = {"values_created": 0, "values_updated": 0}
            _upsert_metric_value(
                metric_definition=definitions[key],
                recorded_at=recorded_at,
                value=value,
                context={"lookback_minutes": lookback_minutes, "window_start": window_start.isoformat()},
                notes="Collected from Nautobot-owned operational records.",
                source=source,
                result=counters,
            )
            result["created"] += counters["values_created"]
            result["updated"] += counters["values_updated"]
        if dryrun:
            transaction.set_rollback(True)
    return result
