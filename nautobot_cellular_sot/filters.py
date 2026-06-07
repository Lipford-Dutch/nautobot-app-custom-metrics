"""Filter sets for Nautobot Cellular SoT."""

import django_filters
from django.db.models import Q
from nautobot.apps.filters import NautobotFilterSet

from nautobot_cellular_sot.models import CarrierProfile, CellularRouter, SIMCard


class CarrierProfileFilterSet(NautobotFilterSet):
    """Filter carrier profiles."""

    q = django_filters.CharFilter(method="search")

    class Meta:
        model = CarrierProfile
        fields = ["name", "carrier_name", "enabled", "roaming_allowed"]

    def search(self, queryset, name, value):
        """Search carrier profile names and APNs."""
        del name
        return queryset.filter(Q(name__icontains=value) | Q(apn__icontains=value))


class CellularRouterFilterSet(NautobotFilterSet):
    """Filter cellular routers."""

    class Meta:
        model = CellularRouter
        fields = ["device", "imei", "provisioning_state", "vendor_platform", "external_system_id"]


class SIMCardFilterSet(NautobotFilterSet):
    """Filter SIM cards."""

    class Meta:
        model = SIMCard
        fields = ["iccid", "carrier_profile", "router", "slot", "provisioning_state"]
