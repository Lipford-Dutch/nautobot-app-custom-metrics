"""REST API viewsets for Lipford Nautobot Metrics."""

from nautobot.extras.api.views import NautobotModelViewSet
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lipford_nautobot_metrics import filters, models
from lipford_nautobot_metrics.api import serializers
from lipford_nautobot_metrics.services import get_metric_summaries, ingest_metric_values


class MetricSummaryView(APIView):
    """Read-only API endpoint for dashboard metric summaries."""

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.MetricSummaryResponseSerializer

    def get(self, request):
        """Return current metric summary values."""
        if not request.user.has_perms(
            (
                "lipford_nautobot_metrics.view_metricdefinition",
                "lipford_nautobot_metrics.view_metricvalue",
            )
        ):
            raise PermissionDenied("You do not have permission to view metric summaries.")

        summaries = get_metric_summaries()
        return Response({"count": len(summaries), "results": summaries})


class MetricIngestView(APIView):
    """Atomic, authenticated bulk-ingestion endpoint."""

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.MetricIngestRequestSerializer

    def post(self, request):
        """Validate and upsert a batch of metric observations."""
        if not request.user.has_perm("lipford_nautobot_metrics.add_metricvalue"):
            raise PermissionDenied("You do not have permission to ingest metric values.")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = ingest_metric_values(serializer.validated_data["values"])
        except ValueError as error:
            raise ValidationError({"values": str(error)}) from error
        return Response(serializers.MetricIngestResponseSerializer(result).data)


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
