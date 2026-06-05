"""UI views for Lipford Nautobot Metrics."""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.ui import object_detail
from nautobot.core.ui.choices import SectionChoices

from lipford_nautobot_metrics import filters, forms, models, tables
from lipford_nautobot_metrics.api import serializers
from lipford_nautobot_metrics.services import get_metric_summaries


class MetricsDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Dashboard view for custom metric summaries."""

    template_name = "lipford_nautobot_metrics/dashboard.html"
    permission_required = (
        "lipford_nautobot_metrics.view_metricdefinition",
        "lipford_nautobot_metrics.view_metricvalue",
    )
    raise_exception = True

    def get_context_data(self, **kwargs):
        """Build dashboard context."""
        context = super().get_context_data(**kwargs)
        summaries = get_metric_summaries()
        context.update(
            {
                "title": "Metrics Dashboard",
                "metric_summaries": summaries,
                "definition_count": len(summaries),
                "value_count": sum(summary["value_count"] for summary in summaries),
            }
        )
        return context


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
