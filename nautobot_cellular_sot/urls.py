"""UI URLs for Nautobot Cellular SoT."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from nautobot_cellular_sot import views

router = NautobotUIViewSetRouter()
router.register("carrier-profiles", views.CarrierProfileUIViewSet)
router.register("cellular-routers", views.CellularRouterUIViewSet)
router.register("sim-cards", views.SIMCardUIViewSet)

app_name = "nautobot_cellular_sot"
urlpatterns = [
    path("", views.CellularDashboardView.as_view(), name="dashboard"),
    path("docs/", RedirectView.as_view(url=static("nautobot_cellular_sot/docs/index.html")), name="docs"),
]
urlpatterns += router.urls
