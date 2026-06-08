"""App configuration tests for Lipford Nautobot Metrics."""

from django.test import SimpleTestCase

from lipford_nautobot_metrics import LipfordNautobotMetricsConfig, config
from lipford_nautobot_metrics.graphql.types import MetricDefinitionType, MetricValueType, graphql_types
from lipford_nautobot_metrics.jobs import SeedSampleMetricData, jobs


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

    def test_jobs_are_registered(self):
        """The job module exposes the registered app jobs."""
        self.assertEqual(jobs, [SeedSampleMetricData])
