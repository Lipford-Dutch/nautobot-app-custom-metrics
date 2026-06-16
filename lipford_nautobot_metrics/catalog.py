"""Canonical full metric catalog definitions."""

from collections import Counter
from typing import Any


def metric(
    key: str,
    name: str,
    category: str,
    unit: str,
    description: str,
    formula: str = "",
    *,
    bounded: bool = False,
    enabled: bool = True,
) -> dict[str, Any]:
    """Build one immutable-style catalog definition."""
    return {
        "key": key,
        "name": name,
        "category": category,
        "kind": key,
        "unit": unit,
        "description": description,
        "formula": formula,
        "bounded": bounded,
        "enabled": enabled,
    }


METRIC_CATALOG: tuple[dict[str, Any], ...] = (
    metric(
        "time_saved_per_automated_task",
        "Time Saved per Automated Task",
        "roi",
        "hours",
        "Time saved by automating a repeatable task.",
        "Time_Manual - Time_Automated",
    ),
    metric(
        "manual_error_rate_reduction",
        "Reduction in Manual Error Rates",
        "roi",
        "percent",
        "Reduction in errors after automation.",
        "(Error_Rate_Manual - Error_Rate_Automated) / Error_Rate_Manual * 100",
        bounded=True,
    ),
    metric(
        "increased_task_throughput",
        "Increased Task Throughput",
        "roi",
        "percent",
        "Increase in task volume after automation.",
        "(Automated - Manual) / Manual * 100",
    ),
    metric(
        "automation_adoption_rate",
        "Automation Adoption Rate",
        "roi",
        "percent",
        "Share of target work executed through automation.",
        "Automated / Potential * 100",
        bounded=True,
    ),
    metric(
        "reduced_operational_costs",
        "Reduced Operational Costs",
        "roi",
        "dollars",
        "Operational expenditure reduction attributable to automation.",
        "(Labor_Before - Labor_After) + (Incident_Before - Incident_After)",
    ),
    metric(
        "cost_avoidance",
        "Cost Avoidance",
        "roi",
        "dollars",
        "Estimated costs avoided through preventative controls.",
        "Sum(Potential_Cost * Likelihood_Reduction)",
    ),
    metric(
        "reduced_tooling_costs",
        "Reduced Tooling Costs",
        "roi",
        "dollars",
        "Savings from tool consolidation and retirement.",
    ),
    metric(
        "cost_of_inaction", "Cost of Inaction", "roi", "dollars", "Estimated cost of continuing without automation."
    ),
    metric(
        "deployment_frequency", "Deployment Frequency", "roi", "count", "Number of successful deployments in a period."
    ),
    metric(
        "change_failure_rate",
        "Change Failure Rate",
        "roi",
        "percent",
        "Percentage of changes causing failure.",
        "Failed_Changes / Total_Changes * 100",
        bounded=True,
    ),
    metric(
        "mean_time_to_recovery",
        "Mean Time to Recovery (MTTR)",
        "roi",
        "hours",
        "Average time to recover from service-impacting failures.",
    ),
    metric(
        "predeployment_validation_time_reduction",
        "Reduction in Pre-Deployment Validation Time",
        "roi",
        "hours",
        "Time reduction from automated pre-deployment validation.",
    ),
    metric(
        "improved_service_delivery_time",
        "Improved Service Delivery Time",
        "business_impact",
        "percent",
        "Reduction in service-delivery cycle time.",
        bounded=True,
    ),
    metric(
        "compliance_posture_audit_cost_reduction",
        "Enhanced Compliance Posture and Reduced Audit Costs",
        "business_impact",
        "dollars",
        "Audit and compliance cost reduction.",
    ),
    metric(
        "increased_innovation_capacity",
        "Increased Innovation Capacity",
        "business_impact",
        "hours",
        "Engineering capacity redirected to higher-value work.",
    ),
    metric(
        "incident_mttr_reduction",
        "Reduced MTTR for Incidents",
        "business_impact",
        "hours",
        "Incident-resolution time reduction attributable to Nautobot.",
    ),
    metric(
        "login_success_count",
        "Successful Logins",
        "user_activity",
        "count",
        "Successful Nautobot authentication events.",
    ),
    metric(
        "login_failed_count",
        "Failed Login Attempts",
        "user_activity",
        "count",
        "Failed Nautobot authentication events.",
    ),
    metric(
        "active_sessions", "Active User Sessions", "user_activity", "gauge", "Current active authenticated sessions."
    ),
    metric(
        "session_duration", "Session Duration", "user_activity", "seconds", "Observed authenticated session duration."
    ),
    metric(
        "logins_by_principal",
        "Logins by User or Group",
        "user_activity",
        "count",
        "Login volume grouped by user or group.",
    ),
    metric("object_creation_count", "Object Creation Count", "user_activity", "count", "Created Nautobot objects."),
    metric(
        "object_read_count", "Object Read or View Count", "user_activity", "count", "Read or viewed Nautobot objects."
    ),
    metric("object_update_count", "Object Update Count", "user_activity", "count", "Updated Nautobot objects."),
    metric("object_deletion_count", "Object Deletion Count", "user_activity", "count", "Deleted Nautobot objects."),
    metric(
        "page_view_frequency",
        "Feature or Page View Frequency",
        "user_activity",
        "count",
        "Page and feature view volume.",
    ),
    metric(
        "user_initiated_job_count",
        "User-Initiated Job Execution Count",
        "user_activity",
        "count",
        "Jobs initiated interactively by users.",
    ),
    metric("filter_usage_frequency", "Filter Usage Frequency", "user_activity", "count", "Filter usage volume."),
    metric("data_export_frequency", "Data Export Frequency", "user_activity", "count", "Data export operations."),
    metric(
        "page_task_duration",
        "Time Spent on Page or Task",
        "user_activity",
        "seconds",
        "Observed page or task duration.",
    ),
    metric(
        "user_task_completion_rate",
        "User Task Completion Rate",
        "user_activity",
        "rate",
        "Share of started user tasks completed.",
        bounded=True,
    ),
    metric(
        "user_activity_score",
        "Most Active Users or Groups",
        "user_activity",
        "score",
        "Composite user or group activity score.",
    ),
    metric(
        "golden_config_compliance_overall",
        "Golden Config Overall Compliance Status",
        "plugin_golden_config",
        "percent",
        "Overall configuration compliance percentage.",
        bounded=True,
    ),
    metric(
        "golden_config_drift_count",
        "Golden Config Compliance Drift Count",
        "plugin_golden_config",
        "count",
        "Detected configuration drift observations.",
    ),
    metric(
        "golden_config_drift_detection_time",
        "Golden Config Time to Detect Drift",
        "plugin_golden_config",
        "seconds",
        "Time required to detect configuration drift.",
    ),
    metric(
        "golden_config_remediation_attempts",
        "Golden Config Automated Remediation Attempts",
        "plugin_golden_config",
        "count",
        "Automated remediation attempts.",
    ),
    metric(
        "golden_config_remediation_success_rate",
        "Golden Config Automated Remediation Success Rate",
        "plugin_golden_config",
        "rate",
        "Successful automated remediation share.",
        bounded=True,
    ),
    metric(
        "golden_config_manual_remediation_count",
        "Golden Config Manual Remediation Count",
        "plugin_golden_config",
        "count",
        "Remediations requiring manual intervention.",
    ),
    metric(
        "golden_config_backup_status_rate",
        "Golden Config Backup Status",
        "plugin_golden_config",
        "rate",
        "Configuration backup outcomes.",
        bounded=True,
    ),
    metric(
        "golden_config_noncompliance_reasons",
        "Golden Config Non-Compliance Reasons",
        "plugin_golden_config",
        "count",
        "Non-compliance observations grouped by reason.",
    ),
    metric(
        "ssot_sync_job_frequency",
        "SSoT Data Synchronization Job Frequency",
        "plugin_ssot",
        "count",
        "SSoT synchronization job executions.",
    ),
    metric(
        "ssot_sync_job_duration",
        "SSoT Data Synchronization Job Duration",
        "plugin_ssot",
        "seconds",
        "SSoT synchronization job duration.",
    ),
    metric(
        "ssot_sync_job_status_rate",
        "SSoT Synchronization Job Success or Failure Rate",
        "plugin_ssot",
        "rate",
        "SSoT synchronization outcomes.",
        bounded=True,
    ),
    metric(
        "ssot_discrepancy_detected_count",
        "SSoT Discrepancies Detected",
        "plugin_ssot",
        "count",
        "Detected source-of-truth discrepancies.",
    ),
    metric(
        "ssot_discrepancy_resolved_automated_count",
        "SSoT Discrepancies Automatically Resolved",
        "plugin_ssot",
        "count",
        "Automatically reconciled discrepancies.",
    ),
    metric(
        "ssot_reconciliation_time",
        "SSoT Discrepancy Reconciliation Time",
        "plugin_ssot",
        "seconds",
        "Time required to reconcile discrepancies.",
    ),
    metric("ssot_data_staleness", "SSoT Data Staleness", "plugin_ssot", "hours", "Age of synchronized source data."),
    metric(
        "ssot_objects_changed_count",
        "Objects Created, Updated, or Deleted by SSoT",
        "plugin_ssot",
        "count",
        "Objects changed by SSoT jobs.",
    ),
    metric(
        "dlm_provisioning_duration",
        "DLM Time to Provision New Device",
        "plugin_dlm",
        "seconds",
        "Device provisioning duration.",
    ),
    metric(
        "dlm_devices_by_stage",
        "DLM Devices per Lifecycle Stage",
        "plugin_dlm",
        "gauge",
        "Devices currently in each lifecycle stage.",
    ),
    metric(
        "dlm_transition_error_count",
        "DLM Lifecycle Transition Errors",
        "plugin_dlm",
        "count",
        "Errors during lifecycle transitions.",
    ),
    metric(
        "dlm_process_adherence_rate",
        "DLM Lifecycle Process Adherence",
        "plugin_dlm",
        "rate",
        "Adherence to lifecycle processes.",
        bounded=True,
    ),
    metric(
        "dlm_stage_duration",
        "DLM Time Spent in Lifecycle Stage",
        "plugin_dlm",
        "days",
        "Time spent in a lifecycle stage.",
    ),
    metric(
        "dlm_stage_automation_rate",
        "DLM Automation Rate per Lifecycle Stage",
        "plugin_dlm",
        "rate",
        "Automated lifecycle-stage task share.",
        bounded=True,
    ),
    metric(
        "job_execution_total_count", "Job Volume or Count", "job_execution", "count", "Total Nautobot job executions."
    ),
    metric(
        "job_execution_status_rate", "Job Results", "job_execution", "rate", "Job execution outcomes.", bounded=True
    ),
    metric(
        "job_execution_duration", "Job Execution Time", "job_execution", "seconds", "Observed job execution duration."
    ),
    metric(
        "job_execution_throughput", "Job Throughput", "job_execution", "count", "Job executions completed per minute."
    ),
    metric(
        "job_resource_consumption",
        "Resource Consumption per Job",
        "job_execution",
        "bytes",
        "Job resource consumption observation.",
    ),
    metric(
        "job_scheduling_delay",
        "Job Scheduling Delay",
        "job_execution",
        "seconds",
        "Delay between scheduling and execution.",
    ),
)

CATALOG_BY_KEY = {definition["key"]: definition for definition in METRIC_CATALOG}
BOUNDED_METRIC_KINDS = {definition["kind"] for definition in METRIC_CATALOG if definition["bounded"]}
EXPECTED_CATEGORY_COUNTS = {
    "roi": 12,
    "business_impact": 4,
    "user_activity": 16,
    "plugin_golden_config": 8,
    "plugin_ssot": 8,
    "plugin_dlm": 6,
    "job_execution": 6,
}
EXPECTED_METRIC_COUNT = sum(EXPECTED_CATEGORY_COUNTS.values())


def get_catalog_category_counts() -> dict[str, int]:
    """Return metric counts by canonical category."""
    return dict(sorted(Counter(definition["category"] for definition in METRIC_CATALOG).items()))


def validate_catalog_saturation() -> None:
    """Raise an error if the canonical catalog is not fully saturated."""
    keys = [definition["key"] for definition in METRIC_CATALOG]
    duplicate_keys = sorted({key for key in keys if keys.count(key) > 1})
    if duplicate_keys:
        raise ValueError(f"Duplicate metric keys: {', '.join(duplicate_keys)}.")

    if len(METRIC_CATALOG) != EXPECTED_METRIC_COUNT:
        raise ValueError(f"Expected {EXPECTED_METRIC_COUNT} metrics, found {len(METRIC_CATALOG)}.")

    category_counts = get_catalog_category_counts()
    if category_counts != EXPECTED_CATEGORY_COUNTS:
        raise ValueError(f"Expected category counts {EXPECTED_CATEGORY_COUNTS}, found {category_counts}.")
