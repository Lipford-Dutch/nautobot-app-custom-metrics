# Full Metric Catalog

The app defines the complete metric catalog in Python and exposes every enabled
definition through the dashboard, REST API, and sample-data job.

## Catalog Coverage

| Area | Metric count |
| --- | ---: |
| ROI and business impact | 16 |
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

## Populate Definitions

Run the **Seed Full Metric Catalog Sample Data** Nautobot Job to create or
repair all definitions and populate deterministic sample observations. The job
is idempotent and supports dry-run validation.

```shell
nautobot-server runjob lipford_nautobot_metrics.jobs.SeedSampleMetricData \
  --data '{"dryrun": false, "sample_days": 3}'
```

## API Access

Use the metric summary endpoint for the latest rollup of every enabled metric:

```text
/api/plugins/lipford-nautobot-metrics/metric-summary/
```

Use the metric definition and value endpoints for complete metadata and
historical observations:

```text
/api/plugins/lipford-nautobot-metrics/metric-definitions/
/api/plugins/lipford-nautobot-metrics/metric-values/
```

## Collection Sources

The sample job proves definition, validation, storage, dashboard, and API
behavior. Production collectors should write observations with a distinct
`source` value and preserve the stable catalog key. Native collectors for
audit events and external apps require those systems to be installed and
configured.
