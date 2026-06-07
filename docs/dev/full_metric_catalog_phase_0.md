# Full Metric Catalog Phase 0

## Objective

Phase 0 inventories and normalizes the complete attached Nautobot metrics guide
before expanding runtime models, collectors, APIs, or dashboards.

The source guide combines several different artifact types:

- Formally defined business and ROI metrics with formulas.
- Formally named telemetry, plugin, and job-execution metrics.
- Dashboard aliases and aggregations derived from canonical metrics.
- Conceptual metrics that require external systems or additional data modeling.

Runtime behavior is intentionally unchanged during this phase.

## Existing Implementation

The application already implements the first four Section 2.1 ROI metrics:

| Existing application key | Canonical catalog name |
| --- | --- |
| `time_saved_per_automated_task` | `nautobot.roi.efficiency_gains.task_automation.time_saved.hours` |
| `manual_error_rate_reduction` | `nautobot.roi.efficiency_gains.manual_error_reduction.percentage` |
| `increased_task_throughput` | No single canonical source name; retain as an application-level derived metric |
| `automation_adoption_rate` | `nautobot.roi.efficiency_gains.automation_adoption.percentage` |

Existing keys remain supported for backward compatibility. A later phase can add
canonical catalog identifiers without changing API consumers.

## Catalog Scope

The guide defines 60 primary metric entries:

| Area | Primary entries | Proposed category key |
| --- | ---: | --- |
| ROI efficiency, cost, automation value, and business impact | 16 | `roi` and `business_impact` |
| User authentication, sessions, CRUD, features, and engagement | 16 | `user_activity` |
| Golden Configuration | 8 | `plugin_golden_config` |
| SSoT | 8 | `plugin_ssot` |
| Device Lifecycle Management | 6 | `plugin_dlm` |
| Generic plugin and job execution | 6 | `job_execution` |

The dashboard sections introduce additional aliases, aggregations, and derived
metrics. These are not treated as new canonical definitions when they can be
computed from a primary metric.

## Normalization Rules

1. Canonical metric identifiers use lowercase dot-separated names beginning
   with `nautobot.`.
2. The final identifier segment describes the measurement or aggregation:
   `count`, `gauge`, `rate`, `percentage`, `seconds`, `hours`, `days`,
   `dollars`, `avg`, `max`, `min`, `p95`, `sum`, or `total`.
3. Tags and dimensions belong in observation context, not in metric keys.
4. Aggregations such as average, maximum, and p95 are derived views unless the
   source system only provides the aggregate.
5. Dashboard aliases map to a canonical metric instead of creating duplicate
   definitions.
6. Metrics requiring external financial, incident, CI/CD, infrastructure, or
   forecasting data are disabled until a collector and ownership contract
   exist.
7. User-identifying dimensions must be access-controlled and should prefer
   stable pseudonymous identifiers where detailed attribution is unnecessary.

## Conflicts Requiring Canonical Mapping

| Conflicting source names | Phase 0 canonical choice |
| --- | --- |
| `object.delete.count`, `object.deletion.count` | `nautobot.user_activity.object_management.object.deletion.count` |
| `discrepancy.resolved_automated.count`, `discrepancy.resolved.automated.count` | `nautobot.plugin_ssot.discrepancy.resolved_automated.count` |
| `stage.duration.days.avg`, `stage.duration.avg.days` | `nautobot.plugin_dlm.stage.duration.days.avg` |
| `remediation.automated_success.rate`, `remediation.automated.success.rate` | `nautobot.plugin_golden_config.remediation.automated_success.rate` |
| `job_execution.total.count`, `job_execution.generic.total.count` | `nautobot.job_execution.total.count` with `plugin_name` and `job_name` context |
| `job_execution.status.rate`, `job_execution.generic.status.rate` | `nautobot.job_execution.status.rate` |
| `job_execution.duration.seconds`, `job_execution.generic.duration.seconds.avg` | Store duration observations under `nautobot.job_execution.duration.seconds`; derive aggregates |
| `data.staleness.hours.gauge`, `data.staleness.hours.avg` | Store gauge observations; derive averages |

## Proposed Units

The existing unit choices must expand in a later phase:

- `count`
- `dollars`
- `seconds`
- `hours`
- `days`
- `percent`
- `rate`
- `bytes`
- `score`

The catalog must distinguish bounded percentages from unbounded percent-change
metrics and ratios.

## Collection Ownership Classes

| Class | Source ownership | Examples |
| --- | --- | --- |
| Native Nautobot | Can be collected from core models, logs, sessions, jobs, or object changes | Login counts, CRUD activity, job executions |
| Optional Nautobot App | Collector runs only when the source app is installed | Golden Config, SSoT, DLM |
| Platform observability | Requires Prometheus, application logs, database metrics, or infrastructure telemetry | API latency, CPU, memory, Celery queue length |
| External business system | Requires finance, incident, change, CI/CD, or survey integrations | Cost savings, MTTR, audit cost, innovation capacity |
| Derived/reporting | Calculated from stored observations or external analytics | Averages, p95, top users, forecast metrics |

## Implementation Batches

### Batch 1: User Activity Foundation

Implement native, low-risk counts first:

- Successful and failed logins.
- Object creation, update, and deletion counts.
- User-initiated job execution counts.
- Data export counts.

This batch validates event capture, context dimensions, privacy controls, and
counter-style units.

### Batch 2: Generic Job Execution

- Total job count.
- Job status observations.
- Job duration.
- Scheduling delay.
- Throughput derived from stored observations.

### Batch 3: ROI and Business Value Expansion

- Reduced operational costs.
- Cost avoidance.
- Reduced tooling costs.
- Deployment frequency.
- Change failure rate.
- MTTR and service-delivery metrics.

These definitions remain disabled until external data contracts are configured.

### Batch 4: Optional App Collectors

- Golden Configuration.
- SSoT.
- Device Lifecycle Management.

Collectors must detect app availability and fail gracefully without blocking
Nautobot startup.

### Batch 5: System Performance and External Integrations

- API/application performance.
- Celery, database, and infrastructure telemetry.
- CI/CD and Ansible integrations.
- Data-derived network service health.

### Batch 6: Dashboard and Forecasting Views

- Dashboard aliases and aggregation views.
- Executive, operational, compliance, and security dashboards.
- Forecasting and what-if metrics only after historical data quality is proven.

## Phase 0 Acceptance Criteria

- The complete guide has been classified into primary, alias, derived, and
  conceptual metrics.
- Existing first-batch behavior and keys remain unchanged.
- Naming conflicts have canonical mappings.
- Collection ownership and privacy requirements are explicit.
- Implementation is divided into small, testable batches.
- No runtime model, migration, API, dashboard, or collector behavior changes
  are introduced.

## Phase 1 Entry Criteria

Phase 1 should start with Batch 1 and add only the category, kind, and unit
choices required for the native user-activity foundation. It must include
focused migrations, validation rules, and tests before adding collectors.
