"""Nautobot Jobs for Lipford Nautobot Metrics."""

from nautobot.apps.jobs import DryRunVar, IntegerVar, Job, register_jobs

from lipford_nautobot_metrics.services import (
    DEFAULT_COLLECTOR_LOOKBACK_MINUTES,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_SAMPLE_DAYS,
    MAX_RETENTION_DAYS,
    MAX_SAMPLE_DAYS,
    collect_nautobot_metrics,
    purge_metric_values,
    seed_sample_metrics,
)

name = "Lipford Nautobot Metrics"


class SeedSampleMetricData(Job):
    """Seed deterministic sample metric observations for early dashboard validation."""

    dryrun = DryRunVar(description="Validate the seed operation without committing database changes.")
    sample_days = IntegerVar(
        default=DEFAULT_SAMPLE_DAYS,
        min_value=1,
        max_value=MAX_SAMPLE_DAYS,
        description="Number of daily sample observations to create or update per metric.",
    )

    class Meta:
        """Job metadata."""

        name = "Seed sample metric data"
        description = "Create or update deterministic sample observations for the full metric catalog."
        field_order = ["sample_days", "dryrun"]
        has_sensitive_variables = False

    def run(self, dryrun=False, sample_days=DEFAULT_SAMPLE_DAYS):
        """Run the sample metric seed operation."""
        try:
            result = seed_sample_metrics(sample_days=sample_days, dryrun=dryrun)
        except Exception:
            self.logger.exception("Failed to seed sample metric data.")
            raise

        action = "Validated" if dryrun else "Seeded"
        summary = (
            f"{action} sample metric data: "
            f"{result['definitions_created']} definitions created, "
            f"{result['definitions_updated']} definitions updated, "
            f"{result['values_created']} values created, "
            f"{result['values_updated']} values updated."
        )
        self.logger.info(summary)
        return summary


class CollectNautobotMetrics(Job):
    """Collect JobResult and ObjectChange reference metrics."""

    dryrun = DryRunVar(description="Validate collection without committing observations.")
    lookback_minutes = IntegerVar(
        default=DEFAULT_COLLECTOR_LOOKBACK_MINUTES,
        min_value=1,
        max_value=10080,
        description="Completed Nautobot records to aggregate from the preceding time window.",
    )

    class Meta:
        """Job metadata."""

        name = "Collect Nautobot reference metrics"
        description = "Collect idempotent JobResult and ObjectChange observations."
        field_order = ["lookback_minutes", "dryrun"]
        has_sensitive_variables = False

    def run(self, dryrun=False, lookback_minutes=DEFAULT_COLLECTOR_LOOKBACK_MINUTES):
        """Run native Nautobot reference collectors."""
        result = collect_nautobot_metrics(lookback_minutes=lookback_minutes, dryrun=dryrun)
        action = "Validated" if dryrun else "Collected"
        summary = f"{action} Nautobot metrics: {result['created']} created, {result['updated']} updated."
        self.logger.info(summary)
        return summary


class PurgeMetricValues(Job):
    """Delete metric observations outside the configured retention window."""

    dryrun = DryRunVar(description="Report records eligible for deletion without deleting them.")
    retention_days = IntegerVar(
        default=max(DEFAULT_RETENTION_DAYS, 1),
        min_value=1,
        max_value=MAX_RETENTION_DAYS,
        description="Delete observations older than this many days.",
    )

    class Meta:
        """Job metadata."""

        name = "Purge retained metric values"
        description = "Apply the configured observation retention policy."
        field_order = ["retention_days", "dryrun"]
        has_sensitive_variables = False

    def run(self, dryrun=False, retention_days=1):
        """Run metric observation retention."""
        result = purge_metric_values(retention_days=retention_days, dryrun=dryrun)
        action = "Would delete" if dryrun else "Deleted"
        summary = f"{action} {result['deleted']} metric values older than {result['cutoff'].isoformat()}."
        self.logger.info(summary)
        return summary


jobs = [SeedSampleMetricData, CollectNautobotMetrics, PurgeMetricValues]

register_jobs(*jobs)
