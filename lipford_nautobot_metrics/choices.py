"""Choice sets for Lipford Nautobot Metrics."""

from nautobot.core.choices import ChoiceSet

from lipford_nautobot_metrics.catalog import METRIC_CATALOG


class MetricCategoryChoices(ChoiceSet):
    """High-level full-catalog metric categories."""

    ROI = "roi"
    BUSINESS_IMPACT = "business_impact"
    USER_ACTIVITY = "user_activity"
    PLUGIN_GOLDEN_CONFIG = "plugin_golden_config"
    PLUGIN_SSOT = "plugin_ssot"
    PLUGIN_DLM = "plugin_dlm"
    JOB_EXECUTION = "job_execution"

    CHOICES = (
        (ROI, "Return on Investment"),
        (BUSINESS_IMPACT, "Business Impact"),
        (USER_ACTIVITY, "User Activity"),
        (PLUGIN_GOLDEN_CONFIG, "Golden Configuration"),
        (PLUGIN_SSOT, "Single Source of Truth"),
        (PLUGIN_DLM, "Device Lifecycle Management"),
        (JOB_EXECUTION, "Job Execution"),
    )


class MetricKindChoices(ChoiceSet):
    """Supported full-catalog metric kinds."""

    TIME_SAVED_PER_AUTOMATED_TASK = "time_saved_per_automated_task"
    MANUAL_ERROR_RATE_REDUCTION = "manual_error_rate_reduction"
    INCREASED_TASK_THROUGHPUT = "increased_task_throughput"
    AUTOMATION_ADOPTION_RATE = "automation_adoption_rate"

    CHOICES = tuple((definition["kind"], definition["name"]) for definition in METRIC_CATALOG)


class MetricUnitChoices(ChoiceSet):
    """Units supported by the full metric catalog."""

    HOURS = "hours"
    PERCENT = "percent"
    COUNT = "count"
    DOLLARS = "dollars"
    SECONDS = "seconds"
    DAYS = "days"
    RATE = "rate"
    GAUGE = "gauge"
    BYTES = "bytes"
    SCORE = "score"

    CHOICES = (
        (HOURS, "Hours"),
        (PERCENT, "Percent"),
        (COUNT, "Count"),
        (DOLLARS, "Dollars"),
        (SECONDS, "Seconds"),
        (DAYS, "Days"),
        (RATE, "Rate"),
        (GAUGE, "Gauge"),
        (BYTES, "Bytes"),
        (SCORE, "Score"),
    )
