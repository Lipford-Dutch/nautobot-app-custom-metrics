# Full Metric Catalog

The app defines the complete metric catalog in Python and exposes every enabled
definition through the dashboard, REST API, and sample-data job.

## Catalog Coverage

| Area | Metric count |
| --- | ---: |
| ROI | 12 |
| Business impact | 4 |
| User activity | 16 |
| Golden Config | 8 |
| SSoT | 8 |
| Device Lifecycle Management | 6 |
| Job execution | 6 |
| **Total** | **60** |

The canonical definitions live in
`lipford_nautobot_metrics/catalog.py`. Each definition declares a stable key,
display name, category, unit, description, optional formula, and whether the
metric is bounded to a maximum value of 100.

The catalog also defines an explicit saturation contract in Python. Tests fail
if the release no longer contains 60 unique metrics with the expected category
counts.

## Populate Definitions

Run the **Seed sample metric data** Nautobot Job to create or
repair all definitions and populate deterministic sample observations. The job
is idempotent and supports dry-run validation.

```shell
nautobot-server runjob lipford_nautobot_metrics.jobs.SeedSampleMetricData \
  --data '{"dryrun": false, "sample_days": 3}'
```

## API Access

Use the metric summary endpoint for the latest rollup of every enabled metric:

```text
/api/plugins/lipford-nautobot-metrics/summary/
```

Use the metric definition and value endpoints for complete metadata and
historical observations:

```text
/api/plugins/lipford-nautobot-metrics/metric-definitions/
/api/plugins/lipford-nautobot-metrics/metric-values/
```

## Collection Sources

The sample job proves definition, validation, storage, dashboard, and API
behavior. Every observation requires a distinct `source` value and preserves
the stable catalog key. Use the **Collect Nautobot reference metrics** Job for
JobResult and ObjectChange observations. External app adapters remain optional
and require their source apps to be installed and configured.

## Bulk Ingestion

Authenticated clients with the `add_metricvalue` permission can atomically
submit observations:

```text
POST /api/plugins/lipford-nautobot-metrics/ingest/
```

```json
{
  "values": [
    {
      "metric_key": "automation_adoption_rate",
      "value": "75.0000",
      "recorded_at": "2026-06-15T12:00:00Z",
      "source": "automation-platform"
    }
  ]
}
```
