# Lipford Nautobot Metrics

Lipford Nautobot Metrics is a custom Nautobot App for tracking business and operational metrics inside Nautobot. The current implementation focuses on two initial ROI metrics: Time Saved per Automated Task and Automation Adoption Rate.

The app provides:

- Metric definition and metric value models with Nautobot UI, filtering, permissions, REST API, custom fields, tags, webhooks, and GraphQL support.
- A sample data Nautobot Job for creating deterministic metric observations.
- A dashboard page at `/plugins/lipford-nautobot-metrics/`.
- A summary API endpoint at `/api/plugins/lipford-nautobot-metrics/summary/`.

## Compatibility

- Nautobot: `>=3.1.0,<4.0.0`
- Python: `>=3.10,<3.15`
- Databases: PostgreSQL and MySQL, following Nautobot support.

## Installation

Install the package in the Nautobot environment:

```shell
pip install lipford-nautobot-metrics
```

Enable the app in `nautobot_config.py`:

```python
PLUGINS = ["lipford_nautobot_metrics"]

PLUGINS_CONFIG = {
    "lipford_nautobot_metrics": {
        "sample_metric_days": 3,
        "sample_metric_source": "lipford_nautobot_metrics.phase2_sample_job",
    }
}
```

Run post-upgrade tasks and restart Nautobot services:

```shell
nautobot-server post_upgrade
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

## Local Development

This project was generated from the official Nautobot App cookiecutter and supports Poetry, Invoke, and Docker development.

Useful commands:

```powershell
.\.venv\Scripts\poetry.exe run ruff check lipford_nautobot_metrics
.\.venv\Scripts\poetry.exe run ruff format --check lipford_nautobot_metrics
```

Docker verification:

```powershell
$env:PATH = 'C:\Program Files\Docker\Docker\resources\bin;' + $env:PATH
$env:NAUTOBOT_VER='3.1.3'
$env:PYTHON_VER='3.12'
.\.venv\Scripts\poetry.exe run invoke start
```

Inside the running Nautobot container:

```shell
nautobot-server check
nautobot-server migrate --check
nautobot-server test lipford_nautobot_metrics.tests --verbosity 2
```

## First Workflow

1. Open Nautobot and confirm the app appears under Installed Apps.
2. Navigate to Metrics > Custom Metrics > Dashboard.
3. Enable the "Seed sample metric data" job from Jobs if needed.
4. Run the job with `sample_days=3`.
5. Review metric definitions, metric values, the dashboard, and the summary API.

## Configuration

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `sample_metric_days` | integer | `3` | Default number of daily sample observations created per metric by the sample data job. Valid range: `1` to `30`. |
| `sample_metric_source` | string | `lipford_nautobot_metrics.phase2_sample_job` | Source label written to sample `MetricValue` records. |

## Verification Status

Current local verification includes:

- Ruff lint and format checks.
- Nautobot system checks.
- Migration checks.
- Docker-backed Nautobot app tests.
- Live API and dashboard smoke checks.

The implemented test suite currently covers model validation, uniqueness constraints, job dry-run/idempotency, dashboard permissions, API permissions, token authentication, and invalid API payload handling.
