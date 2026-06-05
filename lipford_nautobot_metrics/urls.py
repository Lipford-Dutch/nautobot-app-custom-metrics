"""Django urlpatterns declaration for lipford_nautobot_metrics app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from lipford_nautobot_metrics import views

app_name = "lipford_nautobot_metrics"
router = NautobotUIViewSetRouter()

router.register("metric-definitions", views.MetricDefinitionUIViewSet)
router.register("metric-values", views.MetricValueUIViewSet)


urlpatterns = [
    path("", views.MetricsDashboardView.as_view(), name="dashboard"),
    path("docs/", RedirectView.as_view(url=static("lipford_nautobot_metrics/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
