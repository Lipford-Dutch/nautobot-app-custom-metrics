"""App declaration for lipford_nautobot_metrics."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class LipfordNautobotMetricsConfig(NautobotAppConfig):
    """App configuration for the lipford_nautobot_metrics app."""

    name = "lipford_nautobot_metrics"
    verbose_name = "Lipford Nautobot Metrics"
    version = __version__
    author = "Lipford"
    description = "Custom Nautobot app for ROI, activity, and platform metrics."
    base_url = "lipford-nautobot-metrics"
    required_settings = []
    default_settings = {}
    docs_view_name = "plugins:lipford_nautobot_metrics:docs"
    searchable_models = [
        "MetricDefinition",
        "MetricValue",
    ]


config = LipfordNautobotMetricsConfig  # pylint:disable=invalid-name
