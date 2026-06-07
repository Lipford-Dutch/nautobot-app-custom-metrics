"""Model tests for Lipford Nautobot Metrics."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
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
        """Bounded percent metric values are range validated."""
        metric_value = MetricValue(
            metric_definition=self.percent_definition,
            value=Decimal("125.0"),
            recorded_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            metric_value.full_clean()

    def test_percent_value_must_not_be_negative(self):
        """Negative percent metric values are range validated."""
        metric_value = MetricValue(
            metric_definition=self.percent_definition,
            value=Decimal("-1.0"),
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

    def test_percent_change_metric_can_exceed_one_hundred(self):
        """Throughput improvement percentages can exceed one hundred."""
        throughput_definition = MetricDefinition.objects.create(
            name="Increased Task Throughput",
            key="increased_task_throughput",
            category=MetricCategoryChoices.ROI,
            kind=MetricKindChoices.INCREASED_TASK_THROUGHPUT,
            unit=MetricUnitChoices.PERCENT,
        )
        metric_value = MetricValue(
            metric_definition=throughput_definition,
            value=Decimal("400.0"),
            recorded_at=timezone.now(),
        )

        metric_value.full_clean()

    def test_bounded_rate_must_not_exceed_one_hundred(self):
        """Bounded rate metric values are range validated."""
        rate_definition = MetricDefinition.objects.create(
            name="Job Execution Success Rate",
            key="job_execution_status_rate",
            category=MetricCategoryChoices.JOB_EXECUTION,
            kind="job_execution_status_rate",
            unit=MetricUnitChoices.RATE,
        )
        metric_value = MetricValue(
            metric_definition=rate_definition,
            value=Decimal("101.0"),
            recorded_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            metric_value.full_clean()

    def test_duplicate_definition_recorded_source_is_rejected(self):
        """Duplicate values for the same metric, timestamp, and source are rejected."""
        recorded_at = timezone.now()
        MetricValue.objects.create(
            metric_definition=self.percent_definition,
            value=Decimal("75.0"),
            recorded_at=recorded_at,
            source="unit-test",
        )

        with self.assertRaises(IntegrityError):
            MetricValue.objects.create(
                metric_definition=self.percent_definition,
                value=Decimal("80.0"),
                recorded_at=recorded_at,
                source="unit-test",
            )
