"""REST API serializers for Lipford Nautobot Metrics."""

from nautobot.core.api import NautobotModelSerializer
from nautobot.extras.api.mixins import TaggedModelSerializerMixin

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
