"""REST API URL routes for Lipford Nautobot Metrics."""

from django.urls import path
from nautobot.core.api.routers import OrderedDefaultRouter

from lipford_nautobot_metrics.api import views

router = OrderedDefaultRouter(view_name="Lipford Nautobot Metrics")
router.register("metric-definitions", views.MetricDefinitionViewSet)
router.register("metric-values", views.MetricValueViewSet)

app_name = "lipford_nautobot_metrics-api"
urlpatterns = [
    path("summary/", views.MetricSummaryView.as_view(), name="metric-summary"),
]

urlpatterns += router.urls
