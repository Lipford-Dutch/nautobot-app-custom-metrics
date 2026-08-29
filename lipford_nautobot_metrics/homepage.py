"""Nautobot home-page content for metrics operations."""

from nautobot.apps.ui import HomePageItem, HomePagePanel

from lipford_nautobot_metrics.models import MetricDefinition, MetricValue

layout = (
    HomePagePanel(
        name="Metrics",
        weight=850,
        items=(
            HomePageItem(
                name="Metric Definitions",
                link="plugins:lipford_nautobot_metrics:metricdefinition_list",
                model=MetricDefinition,
                description="Defined operational and business measurements",
                permissions=["lipford_nautobot_metrics.view_metricdefinition"],
                weight=100,
            ),
            HomePageItem(
                name="Metric Values",
                link="plugins:lipford_nautobot_metrics:metricvalue_list",
                model=MetricValue,
                description="Collected and imported observations",
                permissions=["lipford_nautobot_metrics.view_metricvalue"],
                weight=200,
            ),
        ),
    ),
)
