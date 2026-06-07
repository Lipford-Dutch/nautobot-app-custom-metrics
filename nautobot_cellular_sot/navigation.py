"""Navigation menu for Nautobot Cellular SoT."""

from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab
from nautobot.core.ui.choices import NavigationIconChoices, NavigationWeightChoices

menu_items = (
    NavMenuTab(
        name="Wireless Infrastructure",
        icon=NavigationIconChoices.WIRELESS,
        weight=NavigationWeightChoices.APPS + 20,
        groups=(
            NavMenuGroup(
                name="Cellular",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_cellular_sot:dashboard",
                        name="Dashboard",
                        weight=50,
                        permissions=[
                            "nautobot_cellular_sot.view_cellularrouter",
                            "nautobot_cellular_sot.view_simcard",
                        ],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cellular_sot:cellularrouter_list",
                        name="Cellular Routers",
                        weight=100,
                        permissions=["nautobot_cellular_sot.view_cellularrouter"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_cellular_sot:cellularrouter_add",
                                permissions=["nautobot_cellular_sot.add_cellularrouter"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cellular_sot:simcard_list",
                        name="SIM Cards",
                        weight=200,
                        permissions=["nautobot_cellular_sot.view_simcard"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_cellular_sot:carrierprofile_list",
                        name="Carrier Profiles",
                        weight=300,
                        permissions=["nautobot_cellular_sot.view_carrierprofile"],
                    ),
                ),
            ),
        ),
    ),
)
