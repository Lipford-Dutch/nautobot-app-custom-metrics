"""Choice sets for Lipford Nautobot Metrics."""

from nautobot.core.choices import ChoiceSet


class MetricCategoryChoices(ChoiceSet):
    """High-level metric categories from the metrics definition."""

    ROI = "roi"

    CHOICES = ((ROI, "Return on Investment"),)


class MetricKindChoices(ChoiceSet):
    """Supported v1 first-batch metric kinds."""

    TIME_SAVED_PER_AUTOMATED_TASK = "time_saved_per_automated_task"
    MANUAL_ERROR_RATE_REDUCTION = "manual_error_rate_reduction"
    INCREASED_TASK_THROUGHPUT = "increased_task_throughput"
    AUTOMATION_ADOPTION_RATE = "automation_adoption_rate"

    CHOICES = (
        (TIME_SAVED_PER_AUTOMATED_TASK, "Time Saved per Automated Task"),
        (MANUAL_ERROR_RATE_REDUCTION, "Reduction in Manual Error Rates"),
        (INCREASED_TASK_THROUGHPUT, "Increased Task Throughput"),
        (AUTOMATION_ADOPTION_RATE, "Automation Adoption Rate"),
    )


class MetricUnitChoices(ChoiceSet):
    """Units supported by Phase 1 metric values."""

    HOURS = "hours"
    PERCENT = "percent"

    CHOICES = (
        (HOURS, "Hours"),
        (PERCENT, "Percent"),
    )
