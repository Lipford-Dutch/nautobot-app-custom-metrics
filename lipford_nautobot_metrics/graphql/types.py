"""GraphQL types for Lipford Nautobot Metrics."""

from nautobot.apps.graphql import OptimizedNautobotObjectType

from lipford_nautobot_metrics.models import MetricDefinition, MetricValue


class MetricDefinitionType(OptimizedNautobotObjectType):
    """GraphQL type for metric definitions."""

    class Meta:
        """GraphQL model options."""

        model = MetricDefinition


class MetricValueType(OptimizedNautobotObjectType):
    """GraphQL type for metric values."""

    class Meta:
        """GraphQL model options."""

        model = MetricValue


graphql_types = [MetricDefinitionType, MetricValueType]
