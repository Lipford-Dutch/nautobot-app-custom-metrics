"""Forms for Lipford Nautobot Metrics."""

from django import forms
from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.forms import (
    DynamicModelChoiceField,
    StaticSelect2,
    StaticSelect2Multiple,
    TagFilterField,
    add_blank_choice,
)
from nautobot.extras.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from lipford_nautobot_metrics import choices, models


class MetricDefinitionForm(NautobotModelForm):
    """Create and edit form for metric definitions."""

    class Meta:
        """Form options."""

        model = models.MetricDefinition
        fields = "__all__"


class MetricDefinitionFilterForm(NautobotFilterForm):
    """Filter form for metric definitions."""

    model = models.MetricDefinition
    q = forms.CharField(required=False, label="Search")
    category = forms.MultipleChoiceField(
        choices=choices.MetricCategoryChoices,
        required=False,
        widget=StaticSelect2Multiple(),
    )
    kind = forms.MultipleChoiceField(
        choices=choices.MetricKindChoices,
        required=False,
        widget=StaticSelect2Multiple(),
    )
    unit = forms.MultipleChoiceField(
        choices=choices.MetricUnitChoices,
        required=False,
        widget=StaticSelect2Multiple(),
    )
    enabled = forms.NullBooleanField(required=False, widget=StaticSelect2())
    tags = TagFilterField(model)


class MetricDefinitionBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    """Bulk edit form for metric definitions."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.MetricDefinition.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False)
    formula = forms.CharField(required=False)
    category = forms.ChoiceField(
        choices=add_blank_choice(choices.MetricCategoryChoices),
        required=False,
        widget=StaticSelect2(),
    )
    kind = forms.ChoiceField(
        choices=add_blank_choice(choices.MetricKindChoices),
        required=False,
        widget=StaticSelect2(),
    )
    unit = forms.ChoiceField(
        choices=add_blank_choice(choices.MetricUnitChoices),
        required=False,
        widget=StaticSelect2(),
    )
    baseline_value = forms.DecimalField(required=False)
    target_value = forms.DecimalField(required=False)
    enabled = forms.NullBooleanField(required=False, widget=StaticSelect2())

    class Meta:
        """Bulk edit options."""

        nullable_fields = ["description", "formula", "baseline_value", "target_value"]


class MetricValueForm(NautobotModelForm):
    """Create and edit form for metric values."""

    metric_definition = DynamicModelChoiceField(queryset=models.MetricDefinition.objects.all())

    class Meta:
        """Form options."""

        model = models.MetricValue
        fields = "__all__"


class MetricValueFilterForm(NautobotFilterForm):
    """Filter form for metric values."""

    model = models.MetricValue
    q = forms.CharField(required=False, label="Search")
    metric_definition = DynamicModelChoiceField(queryset=models.MetricDefinition.objects.all(), required=False)
    source = forms.CharField(max_length=CHARFIELD_MAX_LENGTH, required=False)
    tags = TagFilterField(model)


class MetricValueBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    """Bulk edit form for metric values."""

    pk = forms.ModelMultipleChoiceField(queryset=models.MetricValue.objects.all(), widget=forms.MultipleHiddenInput)
    source = forms.CharField(max_length=CHARFIELD_MAX_LENGTH, required=False)
    notes = forms.CharField(required=False)

    class Meta:
        """Bulk edit options."""

        nullable_fields = ["source", "notes"]
