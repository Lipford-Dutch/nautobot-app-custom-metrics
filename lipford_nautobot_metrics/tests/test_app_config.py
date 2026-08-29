"""App configuration tests for Lipford Nautobot Metrics."""

from django.test import SimpleTestCase
from django.test.client import RequestFactory

from lipford_nautobot_metrics import LipfordNautobotMetricsConfig, config
from lipford_nautobot_metrics.banner import banner
from lipford_nautobot_metrics.graphql.types import MetricDefinitionType, MetricValueType, graphql_types
from lipford_nautobot_metrics.jobs import CollectNautobotMetrics, PurgeMetricValues, SeedSampleMetricData, jobs
from lipford_nautobot_metrics.metrics import METRIC_NAMES


class AppConfigTestCase(SimpleTestCase):
    """Validate Nautobot app registration metadata."""

    def test_config_export_points_to_app_config(self):
        """The package exposes the Nautobot app config class."""
        self.assertIs(config, LipfordNautobotMetricsConfig)

    def test_requested_config_attributes_are_defined(self):
        """The Nautobot app config exposes the expected integration hooks."""
        expected = {
            "name",
            "verbose_name",
            "description",
            "version",
            "author",
            "author_email",
            "base_url",
            "required_settings",
            "default_settings",
            "min_version",
            "max_version",
            "middleware",
            "installed_apps",
            "menu_items",
            "jobs",
            "template_extensions",
            "graphql_types",
            "custom_validators",
            "datasource_contents",
            "caching_config",
        }

        missing = [attribute for attribute in expected if not hasattr(config, attribute)]

        self.assertEqual(missing, [])

    def test_graphql_types_are_registered(self):
        """GraphQL exposes metric definition and value models."""
        self.assertEqual(graphql_types, [MetricDefinitionType, MetricValueType])

    def test_navigation_uses_nautobot_menu_items_hook(self):
        """The app registers navigation through Nautobot's menu_items hook."""
        self.assertEqual(config.menu_items, "navigation.menu_items")

    def test_integration_paths_are_relative_to_the_app(self):
        """Nautobot resolves integration hook paths relative to the app package."""
        self.assertEqual(config.jobs, "jobs.jobs")
        self.assertEqual(config.graphql_types, "graphql.types.graphql_types")

    def test_jobs_are_registered(self):
        """The job module exposes the registered app jobs."""
        self.assertEqual(jobs, [SeedSampleMetricData, CollectNautobotMetrics, PurgeMetricValues])

    def test_production_ui_and_metrics_integrations(self):
        """Production UI and metric integrations expose stable registrations."""
        request = RequestFactory().get("/plugins/lipford-nautobot-metrics/")

        self.assertIsNotNone(banner({"request": request}))
        self.assertEqual(
            METRIC_NAMES,
            ["lipford_nautobot_metric_definitions_total", "lipford_nautobot_metric_values_total"],
        )
        self.assertEqual(
            set(config.constance_config),
            {"collector_lookback_minutes", "max_ingest_batch_size", "retention_days"},
        )
