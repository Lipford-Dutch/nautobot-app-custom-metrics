"""Forms for Nautobot Cellular SoT."""

from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm

from nautobot_cellular_sot.models import CarrierProfile, CellularRouter, SIMCard


class CarrierProfileForm(NautobotModelForm):
    """Carrier profile form."""

    class Meta:
        model = CarrierProfile
        fields = "__all__"


class CellularRouterForm(NautobotModelForm):
    """Cellular router form."""

    class Meta:
        model = CellularRouter
        fields = "__all__"


class SIMCardForm(NautobotModelForm):
    """SIM card form."""

    class Meta:
        model = SIMCard
        fields = "__all__"


class CellularRouterBulkEditForm(NautobotBulkEditForm):
    """Bulk-edit form for cellular routers."""

    model = CellularRouter
    nullable_fields = ["vendor_platform", "external_system_id"]


class CellularRouterFilterForm(NautobotFilterForm):
    """Filter form for cellular routers."""

    model = CellularRouter
