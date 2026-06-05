"""Nautobot Jobs for Lipford Nautobot Metrics."""

from nautobot.apps.jobs import DryRunVar, IntegerVar, Job, register_jobs

from lipford_nautobot_metrics.services import MAX_SAMPLE_DAYS, seed_sample_metrics

name = "Lipford Nautobot Metrics"


class SeedSampleMetricData(Job):
    """Seed deterministic sample metric observations for early dashboard validation."""

    dryrun = DryRunVar(description="Validate the seed operation without committing database changes.")
    sample_days = IntegerVar(
        default=3,
        min_value=1,
        max_value=MAX_SAMPLE_DAYS,
        description="Number of daily sample observations to create or update per metric.",
    )

    class Meta:
        """Job metadata."""

        name = "Seed sample metric data"
        description = "Create or update sample ROI metrics for Time Saved and Automation Adoption Rate."
        field_order = ["sample_days", "dryrun"]
        has_sensitive_variables = False

    def run(self, dryrun=False, sample_days=3):
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


register_jobs(SeedSampleMetricData)
