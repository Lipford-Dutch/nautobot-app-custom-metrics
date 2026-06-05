"""REST API viewsets for Lipford Nautobot Metrics."""

from nautobot.extras.api.views import NautobotModelViewSet

from lipford_nautobot_metrics import filters, models
from lipford_nautobot_metrics.api import serializers


class MetricDefinitionViewSet(NautobotModelViewSet):
    """API viewset for metric definitions."""

    queryset = models.MetricDefinition.objects.all()
    serializer_class = serializers.MetricDefinitionSerializer
    filterset_class = filters.MetricDefinitionFilterSet


class MetricValueViewSet(NautobotModelViewSet):
    """API viewset for metric values."""

    queryset = models.MetricValue.objects.select_related("metric_definition")
    serializer_class = serializers.MetricValueSerializer
    filterset_class = filters.MetricValueFilterSet
