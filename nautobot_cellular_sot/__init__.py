"""Nautobot Cellular SoT app."""

from nautobot.apps import NautobotAppConfig


class NautobotCellularSoTConfig(NautobotAppConfig):
    """App configuration for Nautobot Cellular SoT."""

    name = "nautobot_cellular_sot"
    verbose_name = "Cellular SoT"
    version = "0.1.0"
    author = "Lipford Dutch"
    description = "Authoritative source of truth for cellular routers, SIM cards, and carrier profiles."
    base_url = "cellular-sot"
    api_urls = "nautobot_cellular_sot.api.urls"
    graphql_types = "nautobot_cellular_sot.graphql.types.graphql_types"
    menu_items = "nautobot_cellular_sot.navigation.menu_items"
    template_extensions = "nautobot_cellular_sot.template_content.template_extensions"
    required_settings = []
    min_version = "3.1.0"
    max_version = "4.0.0"
    default_settings = {
        "operational_snapshot_ttl_seconds": 900,
        "sync_batch_size": 500,
        "prometheus_export_enabled": True,
    }
    caching_config = {}


config = NautobotCellularSoTConfig
