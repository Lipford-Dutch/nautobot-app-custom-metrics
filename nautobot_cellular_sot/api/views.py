"""REST API views for Nautobot Cellular SoT."""

from django.http import HttpResponse
from nautobot.apps.api import NautobotModelViewSet
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from nautobot_cellular_sot.api.serializers import (
    CarrierProfileSerializer,
    CellularOperationalSnapshotSerializer,
    CellularRouterSerializer,
    SIMCardSerializer,
)
from nautobot_cellular_sot.filters import CarrierProfileFilterSet, CellularRouterFilterSet, SIMCardFilterSet
from nautobot_cellular_sot.models import CarrierProfile, CellularOperationalSnapshot, CellularRouter, SIMCard
from nautobot_cellular_sot.services import get_cellular_summary


class CellularSummaryView(APIView):
    """Read-only API endpoint for current cellular SoT health."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return aggregate desired and observed cellular state."""
        if not request.user.has_perms(
            (
                "nautobot_cellular_sot.view_cellularrouter",
                "nautobot_cellular_sot.view_simcard",
            )
        ):
            raise PermissionDenied("You do not have permission to view cellular summaries.")
        return Response(get_cellular_summary())


class CellularPrometheusView(APIView):
    """Expose bounded-cardinality latest cellular state in Prometheus text format."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return Prometheus metrics for router registration and conflict state."""
        if not request.user.has_perm("nautobot_cellular_sot.view_cellularrouter"):
            raise PermissionDenied("You do not have permission to view cellular metrics.")
        summary = get_cellular_summary()
        lines = [
            "# HELP cellular_router_info Cellular router inventory marker.",
            "# TYPE cellular_router_info gauge",
            "# HELP cellular_router_registration_up Latest registration status for a cellular router.",
            "# TYPE cellular_router_registration_up gauge",
            "# HELP cellular_router_assignment_conflict Desired SIM assignment conflict marker.",
            "# TYPE cellular_router_assignment_conflict gauge",
        ]
        for router in summary["routers"]:
            device = str(router["device"]).replace("\\", "\\\\").replace('"', '\\"')
            registration_up = 1 if router["registration_state"] in {"registered", "roaming"} else 0
            conflict = 1 if router["assignment_conflict"] else 0
            lines.append(f'cellular_router_info{{device="{device}"}} 1')
            lines.append(f'cellular_router_registration_up{{device="{device}"}} {registration_up}')
            lines.append(f'cellular_router_assignment_conflict{{device="{device}"}} {conflict}')
        return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; version=0.0.4")


class CarrierProfileViewSet(NautobotModelViewSet):
    """REST CRUD for carrier profiles."""

    queryset = CarrierProfile.objects.all()
    serializer_class = CarrierProfileSerializer
    filterset_class = CarrierProfileFilterSet


class CellularRouterViewSet(NautobotModelViewSet):
    """REST CRUD for cellular routers."""

    queryset = CellularRouter.objects.select_related("device", "modem_interface").prefetch_related("sim_cards")
    serializer_class = CellularRouterSerializer
    filterset_class = CellularRouterFilterSet


class SIMCardViewSet(NautobotModelViewSet):
    """REST CRUD for SIM cards."""

    queryset = SIMCard.objects.select_related("carrier_profile", "router__device")
    serializer_class = SIMCardSerializer
    filterset_class = SIMCardFilterSet


class CellularOperationalSnapshotViewSet(NautobotModelViewSet):
    """REST CRUD for latest operational snapshots."""

    queryset = CellularOperationalSnapshot.objects.select_related("router__device")
    serializer_class = CellularOperationalSnapshotSerializer
    filterset_fields = ["router", "registration_state", "collector"]
