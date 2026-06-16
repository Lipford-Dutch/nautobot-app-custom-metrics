# Release v3.0 Forecast

This forecast compares the original metric-catalog requirements with the live
`v0.2.0rc1` implementation. It defines the likely v3.0 feature set and the
acceptance evidence required before publication.

## Live Baseline

The current app provides:

- 60 canonical metric definitions across ROI, business impact, user activity,
  Golden Config, SSoT, Device Lifecycle Management, and Job execution
- Persistent Nautobot storage for metric definitions and observations
- UI, REST API, GraphQL registration, and summary endpoint
- Atomic authenticated bulk ingestion
- Idempotent sample-data Job
- Native Nautobot JobResult and ObjectChange collectors
- Retention Job with dry-run support
- Release automation, checksums, provenance, and repository governance controls

## Source-Requirement Delta

| Requirement Area | Live Status | v3.0 Delta |
| --- | --- | --- |
| Golden Config metrics | Definitions exist; no adapter. | Add optional Golden Config collector and tests. |
| SSoT metrics | Definitions exist; no adapter. | Add optional SSoT collector and reconciliation metrics. |
| DLM metrics | Definitions exist; no adapter. | Add optional Device Lifecycle Management collector. |
| User activity metrics | Some ObjectChange coverage exists. | Add auth/session/page/filter/export activity collectors where Nautobot exposes reliable data. |
| Business ROI metrics | Definitions and ingestion exist. | Add baseline/target governance, import helpers, and calculation explainability. |
| Forecasting | Not implemented. | Add trend, forecast, and threshold surfaces. |
| Retention | Manual Job exists. | Add scheduled retention guidance, rollups, and archive/export path. |
| Production evidence | Alpha/RC evidence exists. | Automate upgrade, rollback, load, and backup/restore validation. |

## Proposed v3.0 Features

### 1. Collector Framework 2.0

Build a pluggable collector registry with consistent scheduling, dry-run,
idempotency, logging, and source provenance.

Acceptance criteria:

- Collectors register through a single interface.
- Every collector supports dry-run and bounded lookback windows.
- Collector failures include source, window, and record-count context.
- Duplicate observations are prevented by metric, timestamp, and source.
- Tests cover idempotency, partial failure, and permission behavior.

### 2. Golden Config Adapter

Collect compliance, drift, remediation, backup, and noncompliance-reason
metrics when the Nautobot Golden Config app is installed.

Acceptance criteria:

- Adapter is disabled when Golden Config is absent.
- Adapter records source as `lipford_nautobot_metrics.golden_config`.
- Collection handles empty data, missing relationships, and failed source jobs.
- Documentation maps each Golden Config metric to its source model or API.

### 3. SSoT Adapter

Collect synchronization job frequency, duration, status, discrepancy,
reconciliation, staleness, and object-change metrics from SSoT job results and
available SSoT records.

Acceptance criteria:

- Adapter is optional and safely no-ops when SSoT is absent.
- Discrepancy metrics distinguish detected, resolved, and unresolved states.
- Staleness calculations document timestamp source and clock assumptions.
- Tests mock SSoT availability and absence.

### 4. Device Lifecycle Management Adapter

Collect provisioning, stage, transition-error, adherence, stage-duration, and
automation-rate metrics when DLM is installed.

Acceptance criteria:

- Adapter maps metrics to DLM objects without hard dependency at import time.
- Stage-duration and stage-count queries are bounded and indexed where needed.
- Missing lifecycle stages are reported as zero observations, not failures.

### 5. User Activity Collector

Expand ObjectChange coverage into user-centric activity metrics where Nautobot
provides reliable data.

Candidate signals:

- Object create/update/delete counts by user
- User-initiated Job counts
- Export events if exposed by Nautobot or middleware
- Login success/failure counts where auth signals are available
- Session counts where Django session data is enabled

Acceptance criteria:

- No sensitive user data is logged.
- User identifiers are configurable for aggregation or anonymization.
- Metrics respect RBAC and audit policy.

### 6. ROI Baseline Governance

Add workflows for managing baselines, targets, owner notes, and calculation
evidence for ROI and business-impact metrics.

Acceptance criteria:

- Operators can document who approved a baseline and when.
- API responses expose baseline and target context.
- Catalog synchronization never overwrites operator-owned fields.
- Release docs explain how ROI values should be audited.

### 7. Forecasting and Thresholds

Add trend, forecast, and threshold views for metrics with enough history.

Acceptance criteria:

- Forecasting is opt-in and documents the calculation method.
- Threshold breaches are visible in UI and API.
- Forecast logic degrades gracefully when data is sparse.
- Tests cover bounded metrics and missing values.

### 8. Retention, Rollup, and Archive

Move from manual retention to an operational data lifecycle model.

Acceptance criteria:

- Retention can be scheduled safely.
- Rollups preserve daily/weekly/monthly trends after raw values expire.
- Archive export is documented before destructive deletion.
- Backup/restore and rollback tests include retained and rolled-up data.

### 9. Production Validation Automation

Convert production-readiness exercises into repeatable CI or release jobs.

Acceptance criteria:

- Upgrade and rollback tests run from published wheels.
- Load tests publish query-count and runtime evidence.
- Release evidence is generated as an artifact.
- Open P0 bugs block release promotion.

### 10. Reporting and Export

Add operator-friendly export and report surfaces for leadership and platform
teams.

Acceptance criteria:

- CSV/JSON export covers definitions, latest values, and historical windows.
- Report output includes source provenance and collection time.
- Exports respect Nautobot permissions.

## v3.0 Release Risks

- Optional app APIs may change independently of this app.
- User activity signals may be incomplete without middleware or audit-log
  integration.
- Forecasting can be misleading without enough history or stable collection
  intervals.
- Large metric-value volumes require retention, rollups, and query budgets.

## Recommended v3.0 Sequence

1. Production validation automation
2. Collector Framework 2.0
3. Golden Config adapter
4. SSoT adapter
5. User Activity collector
6. DLM adapter
7. ROI baseline governance
8. Forecasting and thresholds
9. Retention rollups and archive
10. Reporting and export

