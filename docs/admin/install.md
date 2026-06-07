# Installing the App in Nautobot

## Prerequisites

- Nautobot `>=3.1.0,<4.0.0`
- Python `>=3.10,<3.15`
- PostgreSQL or MySQL, following Nautobot support

The app does not require access to external systems for its current sample-data workflow.

## Install Guide

Install the package in the Nautobot environment:

```shell
pip install lipford-nautobot-metrics
```

To reinstall the app during future Nautobot upgrades, add it to `local_requirements.txt`:

```shell
echo lipford-nautobot-metrics >> local_requirements.txt
```

Enable the app in `nautobot_config.py`:

```python
PLUGINS = ["lipford_nautobot_metrics", "nautobot_cellular_sot"]

PLUGINS_CONFIG = {
    "lipford_nautobot_metrics": {
        "sample_metric_days": 3,
        "sample_metric_source": "lipford_nautobot_metrics.full_catalog_sample_job",
    },
    "nautobot_cellular_sot": {
        "operational_snapshot_ttl_seconds": 900,
        "sync_batch_size": 500,
        "prometheus_export_enabled": True,
    }
}
```

Run Nautobot post-upgrade tasks:

```shell
nautobot-server post_upgrade
```

Restart Nautobot services:

```shell
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

## App Configuration

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `sample_metric_days` | integer | `3` | Default number of daily sample observations created per metric by the sample data job. Valid range: `1` to `30`. |
| `sample_metric_source` | string | `lipford_nautobot_metrics.full_catalog_sample_job` | Source label written to sample `MetricValue` records. |
| `operational_snapshot_ttl_seconds` | integer | `900` | Maximum expected age for latest normalized cellular operational snapshots. |
| `sync_batch_size` | integer | `500` | Maximum number of cellular records processed per bounded synchronization batch. |
| `prometheus_export_enabled` | boolean | `true` | Enables the bounded-cardinality Prometheus text export endpoint. |

## Verification

After installation:

1. Run `nautobot-server check`.
2. Confirm `nautobot-server migrate --check` reports no pending migrations.
3. Confirm the app appears in Nautobot under Installed Apps.
4. Confirm Metrics > Custom Metrics > Dashboard loads.
5. Run the sample data job and confirm metric definitions and values are created.
6. Confirm Wireless Infrastructure > Cellular > Dashboard loads.
