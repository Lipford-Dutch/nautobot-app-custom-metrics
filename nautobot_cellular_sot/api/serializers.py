"""REST serializers for Nautobot Cellular SoT."""

from nautobot.apps.api import NautobotModelSerializer

from nautobot_cellular_sot.models import CarrierProfile, CellularOperationalSnapshot, CellularRouter, SIMCard


class CarrierProfileSerializer(NautobotModelSerializer):
    """Serialize carrier profiles."""

    class Meta:
        model = CarrierProfile
        fields = "__all__"


class CellularRouterSerializer(NautobotModelSerializer):
    """Serialize cellular routers."""

    class Meta:
        model = CellularRouter
        fields = "__all__"


class SIMCardSerializer(NautobotModelSerializer):
    """Serialize SIM cards."""

    class Meta:
        model = SIMCard
        fields = "__all__"


class CellularOperationalSnapshotSerializer(NautobotModelSerializer):
    """Serialize latest operational snapshots."""

    class Meta:
        model = CellularOperationalSnapshot
        fields = "__all__"
