"""Database models for Lipford Nautobot Metrics."""

from django.core.exceptions import ValidationError
from django.db import models
from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models.generics import PrimaryModel
from nautobot.extras.utils import extras_features

from lipford_nautobot_metrics.choices import MetricCategoryChoices, MetricKindChoices, MetricUnitChoices


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class MetricDefinition(PrimaryModel):
    """A named business or operational metric that can be collected over time."""

    natural_key_field_names = ["key"]

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    key = models.SlugField(
        max_length=CHARFIELD_MAX_LENGTH,
        unique=True,
        help_text="Stable machine-readable metric key used by collectors and API clients.",
    )
    category = models.CharField(max_length=CHARFIELD_MAX_LENGTH, choices=MetricCategoryChoices)
    kind = models.CharField(max_length=CHARFIELD_MAX_LENGTH, choices=MetricKindChoices)
    unit = models.CharField(max_length=CHARFIELD_MAX_LENGTH, choices=MetricUnitChoices)
    description = models.TextField(blank=True)
    formula = models.TextField(blank=True, help_text="Human-readable calculation formula for this metric.")
    baseline_value = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    target_value = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        """Model options."""

        ordering = ["name"]
        verbose_name = "Metric Definition"
        verbose_name_plural = "Metric Definitions"

    def __str__(self):
        """Return the display name."""
        return self.name


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class MetricValue(PrimaryModel):
    """A single timestamped observation for a metric definition."""

    natural_key_field_names = ["pk"]

    metric_definition = models.ForeignKey(
        to=MetricDefinition,
        on_delete=models.CASCADE,
        related_name="values",
    )
    value = models.DecimalField(max_digits=18, decimal_places=4)
    recorded_at = models.DateTimeField(db_index=True)
    source = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        help_text="Collector, job, integration, or manual source that produced this observation.",
    )
    context = models.JSONField(
        blank=True,
        default=dict,
        help_text="Optional labels or dimensions, such as task name, team, or automation platform.",
    )
    notes = models.TextField(blank=True)

    class Meta:
        """Model options."""

        ordering = ["-recorded_at", "metric_definition__name"]
        verbose_name = "Metric Value"
        verbose_name_plural = "Metric Values"
        constraints = (
            models.UniqueConstraint(
                fields=("metric_definition", "recorded_at", "source"),
                name="lipford_metrics_unique_definition_recorded_source",
            ),
        )

    def __str__(self):
        """Return a compact display string."""
        return f"{self.metric_definition}: {self.value} {self.metric_definition.unit} at {self.recorded_at:%Y-%m-%d %H:%M:%S}"

    def clean(self):
        """Validate metric observations before saving."""
        super().clean()
        if self.metric_definition_id and self.metric_definition.unit == MetricUnitChoices.PERCENT:
            if self.value < 0:
                raise ValidationError({"value": "Percent metric values must not be negative."})

            bounded_percent_kinds = {
                MetricKindChoices.AUTOMATION_ADOPTION_RATE,
                MetricKindChoices.MANUAL_ERROR_RATE_REDUCTION,
            }
            if self.metric_definition.kind in bounded_percent_kinds and self.value > 100:
                raise ValidationError({"value": "Bounded percent metric values must be between 0 and 100."})
