"""UI views for Lipford Nautobot Metrics."""

from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.ui import object_detail
from nautobot.core.ui.choices import SectionChoices

from lipford_nautobot_metrics import filters, forms, models, tables
from lipford_nautobot_metrics.api import serializers


class MetricDefinitionUIViewSet(NautobotUIViewSet):
    """UI viewset for metric definitions."""

    queryset = models.MetricDefinition.objects.all()
    filterset_class = filters.MetricDefinitionFilterSet
    filterset_form_class = forms.MetricDefinitionFilterForm
    serializer_class = serializers.MetricDefinitionSerializer
    table_class = tables.MetricDefinitionTable
    form_class = forms.MetricDefinitionForm
    bulk_update_form_class = forms.MetricDefinitionBulkEditForm
    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=("name", "key", "category", "kind", "unit", "enabled"),
            ),
            object_detail.ObjectFieldsPanel(
                weight=200,
                section=SectionChoices.RIGHT_HALF,
                fields=("baseline_value", "target_value", "description", "formula"),
            ),
        )
    )


class MetricValueUIViewSet(NautobotUIViewSet):
    """UI viewset for metric values."""

    queryset = models.MetricValue.objects.select_related("metric_definition")
    filterset_class = filters.MetricValueFilterSet
    filterset_form_class = forms.MetricValueFilterForm
    serializer_class = serializers.MetricValueSerializer
    table_class = tables.MetricValueTable
    form_class = forms.MetricValueForm
    bulk_update_form_class = forms.MetricValueBulkEditForm
    object_detail_content = object_detail.ObjectDetailContent(
        panels=(
            object_detail.ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=("metric_definition", "value", "recorded_at", "source"),
            ),
            object_detail.ObjectFieldsPanel(
                weight=200,
                section=SectionChoices.RIGHT_HALF,
                fields=("context", "notes"),
            ),
        )
    )
