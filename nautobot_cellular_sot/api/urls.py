"""REST API URLs for Nautobot Cellular SoT."""

from django.urls import path
from nautobot.apps.api import OrderedDefaultRouter

from nautobot_cellular_sot.api.views import (
    CarrierProfileViewSet,
    CellularOperationalSnapshotViewSet,
    CellularPrometheusView,
    CellularRouterViewSet,
    CellularSummaryView,
    SIMCardViewSet,
)

router = OrderedDefaultRouter()
router.register("carrier-profiles", CarrierProfileViewSet)
router.register("cellular-routers", CellularRouterViewSet)
router.register("sim-cards", SIMCardViewSet)
router.register("operational-snapshots", CellularOperationalSnapshotViewSet)

urlpatterns = router.urls
urlpatterns += [
    path("summary/", CellularSummaryView.as_view(), name="cellular-summary"),
    path("prometheus/", CellularPrometheusView.as_view(), name="cellular-prometheus"),
]
