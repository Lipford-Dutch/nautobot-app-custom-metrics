"""UI views for Nautobot Cellular SoT."""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.ui import object_detail
from nautobot.core.ui.choices import SectionChoices

from nautobot_cellular_sot import filters, forms, models, tables
from nautobot_cellular_sot.api.serializers import CarrierProfileSerializer, CellularRouterSerializer, SIMCardSerializer
from nautobot_cellular_sot.services import get_cellular_summary


class CellularDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Operational dashboard for desired and observed cellular state."""

    template_name = "nautobot_cellular_sot/dashboard.html"
    permission_required = (
        "nautobot_cellular_sot.view_cellularrouter",
        "nautobot_cellular_sot.view_simcard",
    )
    raise_exception = True

    def get_context_data(self, **kwargs):
        """Build dashboard context."""
        context = super().get_context_data(**kwargs)
        summary = get_cellular_summary()
        context.update(
            {
                "title": "Cellular SoT Dashboard",
                "dashboard_stats": (
                    ("Routers", summary["router_count"]),
                    ("Registered", summary["registered_count"]),
                    ("Conflicts", summary["conflict_count"]),
                    ("SIMs", summary["sim_count"]),
                    ("Active SIMs", summary["active_sim_count"]),
                    ("Unassigned", summary["unassigned_sim_count"]),
                ),
                **summary,
            }
        )
        return context


class CarrierProfileUIViewSet(NautobotUIViewSet):
    """CRUD views for carrier profiles."""

    queryset = models.CarrierProfile.objects.all()
    filterset_class = filters.CarrierProfileFilterSet
    form_class = forms.CarrierProfileForm
    table_class = tables.CarrierProfileTable
    serializer_class = CarrierProfileSerializer
    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=("name", "carrier_name", "apn", "authentication_type"),
            ),
            object_detail.ObjectFieldsPanel(
                weight=200,
                section=SectionChoices.RIGHT_HALF,
                fields=("roaming_allowed", "enabled"),
            ),
        )
    )


class CellularRouterUIViewSet(NautobotUIViewSet):
    """CRUD views for cellular routers."""

    queryset = models.CellularRouter.objects.select_related(
        "device", "modem_interface", "modem_inventory_item"
    ).prefetch_related("sim_cards__carrier_profile")
    filterset_class = filters.CellularRouterFilterSet
    filterset_form_class = forms.CellularRouterFilterForm
    form_class = forms.CellularRouterForm
    bulk_update_form_class = forms.CellularRouterBulkEditForm
    table_class = tables.CellularRouterTable
    serializer_class = CellularRouterSerializer
    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=("device", "modem_interface", "modem_inventory_item", "imei"),
            ),
            object_detail.ObjectFieldsPanel(
                weight=200,
                section=SectionChoices.RIGHT_HALF,
                fields=("provisioning_state", "vendor_platform", "external_system_id", "last_reconciled_at"),
            ),
        )
    )


class SIMCardUIViewSet(NautobotUIViewSet):
    """CRUD views for SIM cards."""

    queryset = models.SIMCard.objects.select_related("carrier_profile", "router__device")
    filterset_class = filters.SIMCardFilterSet
    form_class = forms.SIMCardForm
    table_class = tables.SIMCardTable
    serializer_class = SIMCardSerializer
    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=("iccid", "imsi", "msisdn", "carrier_profile"),
            ),
            object_detail.ObjectFieldsPanel(
                weight=200,
                section=SectionChoices.RIGHT_HALF,
                fields=("router", "slot", "provisioning_state", "activated_at", "suspended_at"),
            ),
        )
    )
