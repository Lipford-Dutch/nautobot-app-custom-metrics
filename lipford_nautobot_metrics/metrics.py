"""Bounded-cardinality Prometheus metrics for app health."""

from prometheus_client.metrics_core import GaugeMetricFamily

from lipford_nautobot_metrics.models import MetricDefinition, MetricValue

METRIC_NAMES = ["lipford_nautobot_metric_definitions_total", "lipford_nautobot_metric_values_total"]


def app_inventory_metrics():
    """Yield aggregate app inventory counts."""
    definitions = GaugeMetricFamily(
        "lipford_nautobot_metric_definitions_total", "Number of metric definitions in Nautobot."
    )
    definitions.add_metric([], MetricDefinition.objects.count())
    yield definitions

    values = GaugeMetricFamily("lipford_nautobot_metric_values_total", "Number of stored metric observations.")
    values.add_metric([], MetricValue.objects.count())
    yield values


metrics = [app_inventory_metrics]
