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
    menu_items = "lipford_nautobot_metrics.navigation.menu_items"
    jobs = "lipford_nautobot_metrics.jobs.jobs"
    template_extensions = []
    graphql_types = "lipford_nautobot_metrics.graphql.types.graphql_types"
    custom_validators = []
    datasource_contents = []
    caching_config = {}
    docs_view_name = "plugins:lipford_nautobot_metrics:docs"
    searchable_models = [
        "MetricDefinition",
        "MetricValue",
    ]


config = LipfordNautobotMetricsConfig  # pylint:disable=invalid-name
