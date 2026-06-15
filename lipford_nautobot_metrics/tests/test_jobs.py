"""Job tests for Lipford Nautobot Metrics."""

from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from nautobot.extras.choices import JobResultStatusChoices, ObjectChangeActionChoices
from nautobot.extras.factory import JobResultFactory, ObjectChangeFactory

from lipford_nautobot_metrics.catalog import METRIC_CATALOG
from lipford_nautobot_metrics.choices import MetricKindChoices
from lipford_nautobot_metrics.jobs import CollectNautobotMetrics, PurgeMetricValues, SeedSampleMetricData
from lipford_nautobot_metrics.models import MetricDefinition, MetricValue
from lipford_nautobot_metrics.services import (
    DEFAULT_SAMPLE_DAYS,
    MAX_SAMPLE_DAYS,
    SAMPLE_SOURCE,
    collect_nautobot_metrics,
    get_app_settings,
    get_metric_summaries,
    purge_metric_values,
    seed_sample_metrics,
)


class SeedSampleMetricsTestCase(TestCase):
    """Tests for full-catalog sample metric population."""

    def test_seed_creates_definitions_and_values(self):
        """The seed service creates full-catalog definitions and daily values."""
        result = seed_sample_metrics(sample_days=DEFAULT_SAMPLE_DAYS)
        catalog_size = len(METRIC_CATALOG)

        self.assertEqual(result["definitions_created"], catalog_size)
        self.assertEqual(result["values_created"], catalog_size * DEFAULT_SAMPLE_DAYS)
        self.assertEqual(MetricDefinition.objects.count(), catalog_size)
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), catalog_size * DEFAULT_SAMPLE_DAYS)
        self.assertEqual(
            set(MetricDefinition.objects.values_list("key", flat=True)),
            {definition["key"] for definition in METRIC_CATALOG},
        )

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

        self.assertEqual(result["values_created"], len(METRIC_CATALOG) * 2)
        self.assertEqual(MetricValue.objects.filter(source="unit-test-source").count(), len(METRIC_CATALOG) * 2)

    def test_seed_is_idempotent(self):
        """Running the seed service twice updates existing records instead of duplicating them."""
        seed_sample_metrics(sample_days=2)
        result = seed_sample_metrics(sample_days=2)

        self.assertEqual(result["definitions_created"], 0)
        self.assertEqual(result["values_created"], 0)
        self.assertEqual(MetricDefinition.objects.count(), len(METRIC_CATALOG))
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), len(METRIC_CATALOG) * 2)

    def test_dryrun_rolls_back_writes(self):
        """Dry-run validates the seed path without committing database records."""
        result = seed_sample_metrics(sample_days=2, dryrun=True)

        self.assertEqual(result["definitions_created"], len(METRIC_CATALOG))
        self.assertEqual(result["values_created"], len(METRIC_CATALOG) * 2)
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
        self.assertEqual(MetricValue.objects.filter(source=SAMPLE_SOURCE).count(), len(METRIC_CATALOG))

    def test_job_run_dryrun_returns_summary_without_writes(self):
        """The Nautobot Job dry-run path validates without committing writes."""
        summary = SeedSampleMetricData().run(dryrun=True, sample_days=1)

        self.assertIn("Validated sample metric data", summary)
        self.assertEqual(MetricDefinition.objects.count(), 0)
        self.assertEqual(MetricValue.objects.count(), 0)

    def test_seed_repairs_catalog_metadata_but_preserves_operator_fields(self):
        """Catalog sync repairs app metadata while preserving operator settings."""
        seed_sample_metrics(sample_days=1)
        definition = MetricDefinition.objects.get(key=MetricKindChoices.AUTOMATION_ADOPTION_RATE)
        definition.name = "Drifted name"
        definition.target_value = 72
        definition.enabled = False
        definition.save()

        result = seed_sample_metrics(sample_days=1)

        definition.refresh_from_db()
        self.assertEqual(result["definitions_updated"], 1)
        self.assertEqual(definition.name, "Automation Adoption Rate")
        self.assertEqual(str(definition.target_value), "72.0000")
        self.assertFalse(definition.enabled)

    def test_metric_summaries_exclude_disabled_definitions(self):
        """Dashboard summaries only include enabled metric definitions."""
        seed_sample_metrics(sample_days=1)
        MetricDefinition.objects.filter(key=MetricKindChoices.AUTOMATION_ADOPTION_RATE).update(enabled=False)

        summaries = get_metric_summaries()

        self.assertEqual(len(summaries), len(METRIC_CATALOG) - 1)
        self.assertNotIn(
            MetricKindChoices.AUTOMATION_ADOPTION_RATE,
            {summary["key"] for summary in summaries},
        )

    def test_metric_summaries_use_bounded_query_count(self):
        """Summary generation does not execute a query per metric."""
        seed_sample_metrics(sample_days=1)

        with self.assertNumQueries(1):
            summaries = get_metric_summaries()

        self.assertEqual(len(summaries), len(METRIC_CATALOG))

    def test_retention_dryrun_and_delete(self):
        """Retention reports and then deletes observations older than the cutoff."""
        seed_sample_metrics(sample_days=1)
        MetricValue.objects.update(recorded_at=timezone.now() - timedelta(days=30))

        dryrun = purge_metric_values(retention_days=7, dryrun=True)
        deleted = purge_metric_values(retention_days=7)

        self.assertEqual(dryrun["deleted"], len(METRIC_CATALOG))
        self.assertEqual(deleted["deleted"], len(METRIC_CATALOG))
        self.assertEqual(MetricValue.objects.count(), 0)

    def test_retention_job_dryrun(self):
        """The retention Job exposes a non-destructive validation path."""
        seed_sample_metrics(sample_days=1)
        MetricValue.objects.update(recorded_at=timezone.now() - timedelta(days=30))

        summary = PurgeMetricValues().run(dryrun=True, retention_days=7)

        self.assertIn("Would delete", summary)
        self.assertEqual(MetricValue.objects.count(), len(METRIC_CATALOG))

    def test_registered_jobs_include_production_operations(self):
        """The app exposes collection and retention Jobs."""
        self.assertTrue(CollectNautobotMetrics)
        self.assertTrue(PurgeMetricValues)

    def test_native_collectors_are_idempotent(self):
        """Native collectors aggregate JobResult and ObjectChange data once per window."""
        seed_sample_metrics(sample_days=1)
        completed_at = timezone.now() - timedelta(minutes=5)
        successful_job = JobResultFactory(status=JobResultStatusChoices.STATUS_SUCCESS)
        failed_job = JobResultFactory(status=JobResultStatusChoices.STATUS_FAILURE)
        successful_job.date_started = completed_at - timedelta(seconds=10)
        successful_job.date_done = completed_at
        successful_job.save()
        failed_job.date_started = completed_at - timedelta(seconds=30)
        failed_job.date_done = completed_at
        failed_job.save()
        ObjectChangeFactory(action=ObjectChangeActionChoices.ACTION_CREATE)
        ObjectChangeFactory(action=ObjectChangeActionChoices.ACTION_UPDATE)

        recorded_at = timezone.now().replace(second=0, microsecond=0)
        first = collect_nautobot_metrics(lookback_minutes=60, recorded_at=recorded_at)
        second = collect_nautobot_metrics(lookback_minutes=60, recorded_at=recorded_at)

        self.assertEqual(first, {"created": 6, "updated": 0})
        self.assertEqual(second, {"created": 0, "updated": 0})
        self.assertEqual(
            MetricValue.objects.get(
                metric_definition__key="job_execution_status_rate",
                recorded_at=recorded_at,
            ).value,
            50,
        )

    def test_native_collectors_dryrun(self):
        """Native collection dry-run does not persist observations."""
        seed_sample_metrics(sample_days=1)

        result = collect_nautobot_metrics(lookback_minutes=60, dryrun=True)

        self.assertEqual(result["created"], 6)
        self.assertFalse(
            MetricValue.objects.filter(source__contains="collector").exists(),
        )
