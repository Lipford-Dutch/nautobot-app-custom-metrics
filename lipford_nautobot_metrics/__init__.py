"""App declaration for lipford_nautobot_metrics."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import ConstanceConfigItem, NautobotAppConfig

__version__ = metadata.version(__name__)


class LipfordNautobotMetricsConfig(NautobotAppConfig):
    """App configuration for the lipford_nautobot_metrics app."""

    name = "lipford_nautobot_metrics"
    verbose_name = "Lipford Nautobot Metrics"
    version = __version__
    author = "Lipford"
    author_email = ""
    description = "Custom Nautobot app for ROI, activity, and platform metrics."
    base_url = "lipford-nautobot-metrics"
    required_settings = []
    default_settings = {
        "collector_lookback_minutes": 60,
        "max_ingest_batch_size": 500,
        "retention_days": 0,
        "sample_metric_days": 3,
        "sample_metric_source": "lipford_nautobot_metrics.full_catalog_sample_job",
    }
    min_version = "3.1.0"
    max_version = "4.0.0"
    middleware = []
    installed_apps = []
    menu_items = "navigation.menu_items"
    jobs = "jobs.jobs"
    graphql_types = "graphql.types.graphql_types"
    constance_config = {
        "collector_lookback_minutes": ConstanceConfigItem(60, "Default collection lookback in minutes.", int),
        "max_ingest_batch_size": ConstanceConfigItem(
            500, "Maximum observations accepted by one ingestion request.", int
        ),
        "retention_days": ConstanceConfigItem(0, "Metric retention in days; zero disables automatic retention.", int),
    }
    caching_config = {}
    docs_view_name = "plugins:lipford_nautobot_metrics:docs"
    searchable_models = [
        "MetricDefinition",
        "MetricValue",
    ]

    def ready(self):
        """Register the app and expose stable metric names in long-lived web processes."""
        super().ready()
        from lipford_nautobot_metrics.metrics import METRIC_NAMES

        if "metrics" in self.features and not self.features["metrics"]:
            self.features["metrics"] = METRIC_NAMES.copy()


config = LipfordNautobotMetricsConfig  # pylint:disable=invalid-name
