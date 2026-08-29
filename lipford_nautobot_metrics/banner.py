"""Contextual UI banner for the metrics app."""

from nautobot.apps.ui import Banner


def banner(context):
    """Identify alpha-generated metrics on metrics app pages."""
    request = context["request"]
    if request.path.startswith("/plugins/lipford-nautobot-metrics/"):
        return Banner(
            "Metrics may include seeded observations. Confirm each source before using results for production decisions.",
            banner_class="warning",
        )
    return None
