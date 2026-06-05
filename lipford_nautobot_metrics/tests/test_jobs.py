"""Job tests for Lipford Nautobot Metrics."""

from django.test import TestCase

from lipford_nautobot_metrics.jobs import SeedSampleMetricData
from lipford_nautobot_metrics.models import MetricDefinition, MetricValue
from lipford_nautobot_metrics.services import SAMPLE_SOURCE, seed_sample_metrics


class SeedSampleMetricsTestCase(TestCase):
    """Tests for Phase 2 sample metric population."""

    def test_seed_creates_definitions_and_values(self):
        """The seed service creates two definitions and daily values for each metric."""
        result = seed_sample_metrics(sample_days=3)

        self.assertEqual(result["definitions_created"], 2)
        self.assertEqual(result["values_created"], 6)
        self.assertEqual(MetricDefinition.objects.count(), 2)
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), 6)

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

    def test_job_run_returns_summary(self):
        """The Nautobot Job wrapper returns a useful execution summary."""
        summary = SeedSampleMetricData().run(dryrun=False, sample_days=1)

        self.assertIn("Seeded sample metric data", summary)
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), 2)
