"""Model tests for Lipford Nautobot Metrics."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from lipford_nautobot_metrics.choices import MetricCategoryChoices, MetricKindChoices, MetricUnitChoices
from lipford_nautobot_metrics.models import MetricDefinition, MetricValue


class MetricDefinitionTestCase(TestCase):
    """Tests for metric definitions."""

    def test_str_returns_name(self):
        """The string representation is the definition name."""
        definition = MetricDefinition(
            name="Time Saved per Automated Task",
            key="time_saved_per_automated_task",
            category=MetricCategoryChoices.ROI,
            kind=MetricKindChoices.TIME_SAVED_PER_AUTOMATED_TASK,
            unit=MetricUnitChoices.HOURS,
        )

        self.assertEqual(str(definition), "Time Saved per Automated Task")


class MetricValueTestCase(TestCase):
    """Tests for metric values."""

    def setUp(self):
        """Create shared metric definitions."""
        self.percent_definition = MetricDefinition.objects.create(
            name="Automation Adoption Rate",
            key="automation_adoption_rate",
            category=MetricCategoryChoices.ROI,
            kind=MetricKindChoices.AUTOMATION_ADOPTION_RATE,
            unit=MetricUnitChoices.PERCENT,
        )

    def test_percent_value_must_be_between_zero_and_one_hundred(self):
        """Percent metric values are range validated."""
        metric_value = MetricValue(
            metric_definition=self.percent_definition,
            value=Decimal("125.0"),
            recorded_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            metric_value.full_clean()

    def test_valid_percent_value_cleans(self):
        """A valid percent observation passes validation."""
        metric_value = MetricValue(
            metric_definition=self.percent_definition,
            value=Decimal("75.0"),
            recorded_at=timezone.now(),
        )

        metric_value.full_clean()
