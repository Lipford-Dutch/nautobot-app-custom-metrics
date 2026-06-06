"""FilterSets for Lipford Nautobot Metrics."""

import django_filters
from nautobot.core.filters import NaturalKeyOrPKMultipleChoiceFilter, SearchFilter
from nautobot.extras.filters import NautobotFilterSet

from lipford_nautobot_metrics import choices, models


class MetricDefinitionFilterSet(NautobotFilterSet):
    """Filters for metric definitions."""

    q = SearchFilter(filter_predicates={"name": "icontains", "key": "icontains", "description": "icontains"})
    category = django_filters.MultipleChoiceFilter(choices=choices.MetricCategoryChoices, null_value=None)
    kind = django_filters.MultipleChoiceFilter(choices=choices.MetricKindChoices, null_value=None)
    unit = django_filters.MultipleChoiceFilter(choices=choices.MetricUnitChoices, null_value=None)

    class Meta:
        """FilterSet options."""

        model = models.MetricDefinition
        fields = "__all__"


class MetricValueFilterSet(NautobotFilterSet):
    """Filters for metric values."""

    q = SearchFilter(
        filter_predicates={
            "metric_definition__name": "icontains",
            "metric_definition__key": "icontains",
            "source": "icontains",
            "notes": "icontains",
        }
    )
    metric_definition = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.MetricDefinition.objects.all(),
        to_field_name="key",
    )

    class Meta:
        """FilterSet options."""

        model = models.MetricValue
        fields = "__all__"
