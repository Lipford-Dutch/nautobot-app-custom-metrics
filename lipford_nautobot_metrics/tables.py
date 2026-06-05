"""Tables for Lipford Nautobot Metrics."""

import django_tables2 as tables
from nautobot.core.tables import BaseTable, ButtonsColumn, TagColumn, ToggleColumn

from lipford_nautobot_metrics import models


class MetricDefinitionTable(BaseTable):
    """Table for metric definitions."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    tags = TagColumn(url_name="plugins:lipford_nautobot_metrics:metricdefinition_list")
    actions = ButtonsColumn(models.MetricDefinition)

    class Meta(BaseTable.Meta):
        """Table options."""

        model = models.MetricDefinition
        fields = ("pk", "name", "key", "category", "kind", "unit", "enabled", "tags", "actions")
        default_columns = ("pk", "name", "key", "kind", "unit", "enabled", "actions")


class MetricValueTable(BaseTable):
    """Table for metric values."""

    pk = ToggleColumn()
    metric_definition = tables.Column(linkify=True)
    tags = TagColumn(url_name="plugins:lipford_nautobot_metrics:metricvalue_list")
    actions = ButtonsColumn(models.MetricValue)

    class Meta(BaseTable.Meta):
        """Table options."""

        model = models.MetricValue
        fields = ("pk", "metric_definition", "value", "recorded_at", "source", "tags", "actions")
        default_columns = ("pk", "metric_definition", "value", "recorded_at", "source", "actions")
