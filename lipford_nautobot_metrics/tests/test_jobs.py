"""Job tests for Lipford Nautobot Metrics."""

from django.test import TestCase, override_settings

from lipford_nautobot_metrics.choices import MetricKindChoices
from lipford_nautobot_metrics.jobs import SeedSampleMetricData
from lipford_nautobot_metrics.models import MetricDefinition, MetricValue
from lipford_nautobot_metrics.services import (
    DEFAULT_SAMPLE_DAYS,
    MAX_SAMPLE_DAYS,
    SAMPLE_SOURCE,
    get_app_settings,
    get_metric_summaries,
    seed_sample_metrics,
)


class SeedSampleMetricsTestCase(TestCase):
    """Tests for Phase 2 sample metric population."""

    def test_seed_creates_definitions_and_values(self):
        """The seed service creates two definitions and daily values for each metric."""
        result = seed_sample_metrics(sample_days=DEFAULT_SAMPLE_DAYS)

        self.assertEqual(result["definitions_created"], 2)
        self.assertEqual(result["values_created"], 6)
        self.assertEqual(MetricDefinition.objects.count(), 2)
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), 6)

    def test_app_settings_use_defaults_and_overrides(self):
        """App settings expose defensive defaults and Nautobot config overrides."""
        self.assertEqual(get_app_settings()["sample_metric_days"], DEFAULT_SAMPLE_DAYS)

        with override_settings(
            PLUGINS_CONFIG={
                "lipford_nautobot_metrics": {
                    "sample_metric_days": 2,
                    "sample_metric_source": "unit-test-source",
                }
            }
        ):
            result = seed_sample_metrics()

        self.assertEqual(result["values_created"], 4)
        self.assertEqual(MetricValue.objects.filter(source="unit-test-source").count(), 4)

    def test_seed_is_idempotent(self):
        """Running the seed service twice updates existing records instead of duplicating them."""
        seed_sample_metrics(sample_days=2)
        result = seed_sample_metrics(sample_days=2)

        self.assertEqual(result["definitions_created"], 0)
        self.assertEqual(result["values_created"], 0)
        self.assertEqual(MetricDefinition.objects.count(), 2)
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), 4)

    def test_dryrun_rolls_back_writes(self):
        """Dry-run validates the seed path without committing database records."""
        result = seed_sample_metrics(sample_days=2, dryrun=True)

        self.assertEqual(result["definitions_created"], 2)
        self.assertEqual(result["values_created"], 4)
        self.assertEqual(MetricDefinition.objects.count(), 0)
        self.assertEqual(MetricValue.objects.count(), 0)

    def test_invalid_sample_days_raises_value_error(self):
        """The seed service rejects unsupported sample windows."""
        with self.assertRaises(ValueError):
            seed_sample_metrics(sample_days=0)

        with self.assertRaises(ValueError):
            seed_sample_metrics(sample_days=MAX_SAMPLE_DAYS + 1)

    def test_job_run_returns_summary(self):
        """The Nautobot Job wrapper returns a useful execution summary."""
        summary = SeedSampleMetricData().run(dryrun=False, sample_days=1)

        self.assertIn("Seeded sample metric data", summary)
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), 2)

    def test_job_run_dryrun_returns_summary_without_writes(self):
        """The Nautobot Job dry-run path validates without committing writes."""
        summary = SeedSampleMetricData().run(dryrun=True, sample_days=1)

        self.assertIn("Validated sample metric data", summary)
        self.assertEqual(MetricDefinition.objects.count(), 0)
        self.assertEqual(MetricValue.objects.count(), 0)

    def test_seed_repairs_changed_definition_metadata(self):
        """Existing default metric definitions are repaired when their metadata drifts."""
        seed_sample_metrics(sample_days=1)
        definition = MetricDefinition.objects.get(key=MetricKindChoices.AUTOMATION_ADOPTION_RATE)
        definition.target_value = None
        definition.save()

        result = seed_sample_metrics(sample_days=1)

        definition.refresh_from_db()
        self.assertEqual(result["definitions_updated"], 1)
        self.assertEqual(str(definition.target_value), "60.0000")

    def test_metric_summaries_exclude_disabled_definitions(self):
        """Dashboard summaries only include enabled metric definitions."""
        seed_sample_metrics(sample_days=1)
        MetricDefinition.objects.filter(key=MetricKindChoices.AUTOMATION_ADOPTION_RATE).update(enabled=False)

        summaries = get_metric_summaries()

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0]["key"], MetricKindChoices.TIME_SAVED_PER_AUTOMATED_TASK)
