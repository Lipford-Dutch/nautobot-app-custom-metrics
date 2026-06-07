"""Tables for Nautobot Cellular SoT."""

import django_tables2 as tables
from nautobot.apps.tables import BaseTable, ButtonsColumn

from nautobot_cellular_sot.models import CarrierProfile, CellularRouter, SIMCard


class CarrierProfileTable(BaseTable):
    """Carrier profile table."""

    name = tables.Column(linkify=True)
    actions = ButtonsColumn(CarrierProfile)

    class Meta(BaseTable.Meta):
        model = CarrierProfile
        fields = ("name", "carrier_name", "apn", "roaming_allowed", "enabled")


class CellularRouterTable(BaseTable):
    """Cellular router table."""

    device = tables.Column(linkify=True)
    modem_interface = tables.Column(linkify=True)
    actions = ButtonsColumn(CellularRouter)

    class Meta(BaseTable.Meta):
        model = CellularRouter
        fields = ("device", "modem_interface", "imei", "provisioning_state", "vendor_platform", "last_reconciled_at")


class SIMCardTable(BaseTable):
    """SIM card table with masked sensitive identifiers."""

    masked_iccid = tables.Column(linkify=True, verbose_name="ICCID")
    carrier_profile = tables.Column(linkify=True)
    router = tables.Column(linkify=True)
    actions = ButtonsColumn(SIMCard)

    class Meta(BaseTable.Meta):
        model = SIMCard
        fields = ("masked_iccid", "carrier_profile", "router", "slot", "provisioning_state")
