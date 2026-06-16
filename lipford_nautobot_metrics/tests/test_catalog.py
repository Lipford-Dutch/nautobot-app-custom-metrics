"""Catalog saturation tests for Lipford Nautobot Metrics."""

from django.test import SimpleTestCase

from lipford_nautobot_metrics.catalog import (
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_METRIC_COUNT,
    METRIC_CATALOG,
    get_catalog_category_counts,
    validate_catalog_saturation,
)


class MetricCatalogSaturationTestCase(SimpleTestCase):
    """Tests for the canonical full metric catalog contract."""

    def test_catalog_contains_all_defined_metrics(self):
        """The release catalog contains every defined metric exactly once."""
        validate_catalog_saturation()

        self.assertEqual(len(METRIC_CATALOG), EXPECTED_METRIC_COUNT)
        self.assertEqual(len({definition["key"] for definition in METRIC_CATALOG}), EXPECTED_METRIC_COUNT)
        self.assertEqual(get_catalog_category_counts(), EXPECTED_CATEGORY_COUNTS)

    def test_every_metric_is_dashboard_ready(self):
        """Every metric includes the fields required by dashboard and API consumers."""
        required_fields = {"key", "name", "category", "kind", "unit", "description", "formula", "bounded", "enabled"}

        for definition in METRIC_CATALOG:
            self.assertEqual(set(definition), required_fields)
            self.assertTrue(definition["key"])
            self.assertTrue(definition["name"])
            self.assertTrue(definition["category"])
            self.assertTrue(definition["kind"])
            self.assertTrue(definition["unit"])
