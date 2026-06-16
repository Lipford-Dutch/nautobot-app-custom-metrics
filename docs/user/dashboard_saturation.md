# Dashboard Saturation

Dashboard saturation means every canonical metric definition is present,
enabled, observable, and exposed through the same Nautobot-backed dashboard and
API surfaces.

## Saturation Contract

The v3 release must preserve the complete 60-metric catalog:

| Category | Required definitions |
| --- | ---: |
| ROI | 12 |
| Business Impact | 4 |
| User Activity | 16 |
| Golden Config | 8 |
| SSoT | 8 |
| Device Lifecycle Management | 6 |
| Job Execution | 6 |
| **Total** | **60** |

The application enforces this contract with catalog saturation tests. A release
cannot silently drop a metric key, duplicate a metric key, or change category
counts without changing the explicit catalog contract.

## Dashboard Readiness

The dashboard groups metric summaries by category and shows:

- Enabled definition coverage
- Observation coverage
- Latest value
- Average value
- Target value
- Sample count
- Latest timestamp
- Source

After running the **Seed sample metric data** Job, both dashboard coverage
cards should show `60/60`.

## External Dashboarding

Use the summary API for BI tools, portals, or external dashboards:

```text
/api/plugins/lipford-nautobot-metrics/summary/
```

The summary response includes one result per enabled metric definition. Each
result includes the stable metric key, category, unit, latest value, average,
sample count, target, timestamp, and source.

## Collection Status

Not every metric has a native collector yet. v3 development will add optional
collectors and adapters, but metrics can already be populated through:

- The deterministic sample-data Job
- The atomic ingestion endpoint
- Native JobResult and ObjectChange collectors for supported metrics
- Manual/API writes by authorized operators

