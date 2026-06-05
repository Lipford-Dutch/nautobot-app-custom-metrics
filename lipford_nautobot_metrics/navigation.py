"""Navigation menu items for Lipford Nautobot Metrics."""

from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab
from nautobot.core.ui.choices import NavigationIconChoices, NavigationWeightChoices

menu_items = (
    NavMenuTab(
        name="Metrics",
        icon=NavigationIconChoices.APPS,
        weight=NavigationWeightChoices.APPS + 10,
        groups=(
            NavMenuGroup(
                name="Custom Metrics",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:lipford_nautobot_metrics:dashboard",
                        name="Dashboard",
                        weight=50,
                        permissions=[
                            "lipford_nautobot_metrics.view_metricdefinition",
                            "lipford_nautobot_metrics.view_metricvalue",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:lipford_nautobot_metrics:metricdefinition_list",
                        name="Metric Definitions",
                        weight=100,
                        permissions=["lipford_nautobot_metrics.view_metricdefinition"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:lipford_nautobot_metrics:metricdefinition_add",
                                permissions=["lipford_nautobot_metrics.add_metricdefinition"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:lipford_nautobot_metrics:metricvalue_list",
                        name="Metric Values",
                        weight=200,
                        permissions=["lipford_nautobot_metrics.view_metricvalue"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:lipford_nautobot_metrics:metricvalue_add",
                                permissions=["lipford_nautobot_metrics.add_metricvalue"],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
