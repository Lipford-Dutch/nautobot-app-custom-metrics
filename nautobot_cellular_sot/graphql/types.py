"""GraphQL types for Nautobot Cellular SoT."""

from nautobot.apps.graphql import NautobotObjectType

from nautobot_cellular_sot.models import CarrierProfile, CellularOperationalSnapshot, CellularRouter, SIMCard


class CarrierProfileType(NautobotObjectType):
    """GraphQL type for carrier profiles."""

    class Meta:
        model = CarrierProfile


class CellularRouterType(NautobotObjectType):
    """GraphQL type for cellular routers."""

    class Meta:
        model = CellularRouter


class SIMCardType(NautobotObjectType):
    """GraphQL type for SIM cards."""

    class Meta:
        model = SIMCard


class CellularOperationalSnapshotType(NautobotObjectType):
    """GraphQL type for latest operational snapshots."""

    class Meta:
        model = CellularOperationalSnapshot


graphql_types = [CarrierProfileType, CellularRouterType, SIMCardType, CellularOperationalSnapshotType]
