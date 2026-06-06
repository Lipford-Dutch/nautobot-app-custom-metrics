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
PLUGINS = ["lipford_nautobot_metrics"]

PLUGINS_CONFIG = {
    "lipford_nautobot_metrics": {
        "sample_metric_days": 3,
        "sample_metric_source": "lipford_nautobot_metrics.v1_first_batch_sample_job",
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
| `sample_metric_source` | string | `lipford_nautobot_metrics.v1_first_batch_sample_job` | Source label written to sample `MetricValue` records. |

## Verification

After installation:

1. Run `nautobot-server check`.
2. Confirm `nautobot-server migrate --check` reports no pending migrations.
3. Confirm the app appears in Nautobot under Installed Apps.
4. Confirm Metrics > Custom Metrics > Dashboard loads.
5. Run the sample data job and confirm metric definitions and values are created.
