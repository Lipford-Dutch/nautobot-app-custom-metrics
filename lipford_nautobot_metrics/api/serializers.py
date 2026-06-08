"""REST API serializers for Lipford Nautobot Metrics."""

from nautobot.core.api import NautobotModelSerializer
from nautobot.extras.api.mixins import TaggedModelSerializerMixin
from rest_framework import serializers

from lipford_nautobot_metrics import models


class MetricDefinitionSerializer(TaggedModelSerializerMixin, NautobotModelSerializer):
    """Serializer for metric definitions."""

    class Meta:
        """Serializer options."""

        model = models.MetricDefinition
        fields = "__all__"


class MetricValueSerializer(TaggedModelSerializerMixin, NautobotModelSerializer):
    """Serializer for metric values."""

    class Meta:
        """Serializer options."""

        model = models.MetricValue
        fields = "__all__"


class MetricSummarySerializer(serializers.Serializer):
    """Serializer for dashboard metric summary rows."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    key = serializers.CharField()
    category = serializers.CharField()
    kind = serializers.CharField()
    unit = serializers.CharField()
    target_value = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True)
    value_count = serializers.IntegerField()
    average_value = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True)
    latest_recorded_at = serializers.DateTimeField(allow_null=True)
    latest_value = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True)
    latest_source = serializers.CharField(allow_blank=True)


class MetricSummaryResponseSerializer(serializers.Serializer):
    """Serializer for the metric summary API response."""

    count = serializers.IntegerField()
    results = MetricSummarySerializer(many=True)
