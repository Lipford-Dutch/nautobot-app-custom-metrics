# Lipford Nautobot Metrics

[![Nautobot](https://img.shields.io/badge/Nautobot-3.1%2B-blue)](https://www.networktocode.com/nautobot/)
[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache--2.0-green)](https://github.com/Lipford-Dutch/nautobot-app-custom-metrics/blob/main/LICENSE)

Lipford Nautobot Metrics is a Nautobot 3.1 App for tracking automation ROI, user activity, app, lifecycle, and Job metrics inside Nautobot. It provides a canonical 60-metric catalog, persistent observations, UI and API access, sample data, authenticated bulk ingestion, and native Nautobot reference collectors.

## Repository Metadata

- Package: `lipford-nautobot-metrics`
- Python module: `lipford_nautobot_metrics`
- Nautobot app label: `lipford_nautobot_metrics`
- GitHub repository: `Lipford-Dutch/nautobot-app-custom-metrics`
- License: Apache-2.0
- Development status: Alpha
- Primary audience: Nautobot administrators, network automation engineers, and platform teams

Recommended GitHub repository metadata:

- Description: `Custom Nautobot app for automation ROI, adoption, and platform metrics.`
- Website: `https://github.com/Lipford-Dutch/nautobot-app-custom-metrics/tree/main/docs`
- Topics: `nautobot`, `nautobot-app`, `network-automation`, `metrics`, `roi`, `telemetry`, `django`, `rest-api`

## Features

- Metric definition and metric value models using Nautobot model patterns.
- Full 60-metric catalog across ROI, business impact, user activity, Golden
  Config, SSoT, Device Lifecycle Management, and Job execution.
- Nautobot UI list, detail, filter, dashboard, and navigation integration.
- REST API endpoints under `/api/plugins/lipford-nautobot-metrics/`.
- Summary endpoint for aggregate metric snapshots.
- Source-controlled project wiki for v3 roadmap, operations, and release
  governance.
- Idempotent sample-data Nautobot Job for local verification and demos.
- App configuration schema for collection defaults.
- Tests for models, jobs, views, permissions, API behavior, and invalid payloads.

## Compatibility

| Component | Supported versions |
| --- | --- |
| Nautobot | `>=3.1.0,<4.0.0` |
| Python | `>=3.10,<3.15`; active validation target is `3.14` |
| Database | PostgreSQL or MySQL, following Nautobot support |

The local Docker verification target uses Nautobot `3.1.3` and Python `3.14`.

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
        "sample_metric_source": "lipford_nautobot_metrics.full_catalog_sample_job",
    }
}
```

Run Nautobot post-upgrade tasks and restart Nautobot services:

```shell
nautobot-server post_upgrade
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

For Docker-based deployments, rebuild or restart the Nautobot containers after installing the package and updating `nautobot_config.py`.

## Configuration

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `sample_metric_days` | integer | `3` | Default number of daily sample observations created per metric by the sample data job. Valid range: `1` to `30`. |
| `sample_metric_source` | string | `lipford_nautobot_metrics.full_catalog_sample_job` | Source label written to sample `MetricValue` records. |

## First Workflow

1. Start Nautobot with the app enabled.
2. Confirm the app appears in **Installed Apps**.
3. Navigate to **Metrics > Custom Metrics > Dashboard**.
4. Enable and run the **Seed sample metric data** job with `sample_days=3`.
5. Review metric definitions, metric values, the dashboard, and the summary API.

## API

The app registers these REST API routes:

| Endpoint | Purpose |
| --- | --- |
| `/api/plugins/lipford-nautobot-metrics/metric-definitions/` | Metric definition CRUD |
| `/api/plugins/lipford-nautobot-metrics/metric-values/` | Metric value CRUD |
| `/api/plugins/lipford-nautobot-metrics/summary/` | Aggregate metric summary |
| `/api/plugins/lipford-nautobot-metrics/ingest/` | Atomic authenticated bulk ingestion |

Example summary request:

```shell
curl -H "Authorization: Token ${NAUTOBOT_TOKEN}" \
  http://localhost:8080/api/plugins/lipford-nautobot-metrics/summary/
```

## Local Development

This project was generated from the official Nautobot App cookiecutter and supports Poetry, Invoke, and Docker development.

Prepare the Docker environment on Windows PowerShell:

```powershell
$env:PATH = 'C:\Program Files\Docker\Docker\resources\bin;' + $env:PATH
$env:NAUTOBOT_VER='3.1.3'
$env:PYTHON_VER='3.14'
```

Start the development stack:

```powershell
.\.venv\Scripts\poetry.exe run invoke start
```

Run quality checks:

```powershell
.\.venv\Scripts\poetry.exe run ruff check lipford_nautobot_metrics
.\.venv\Scripts\poetry.exe run ruff format --check lipford_nautobot_metrics
.\.venv\Scripts\poetry.exe check
.\.venv\Scripts\poetry.exe build
.\.venv\Scripts\poetry.exe run mkdocs build --strict
```

Run Nautobot checks and tests inside the running container:

```powershell
docker compose --project-name lipford_nautobot_metrics `
  -f development/docker-compose.base.yml `
  -f development/docker-compose.redis.yml `
  -f development/docker-compose.postgres.yml `
  -f development/docker-compose.dev.yml `
  exec -T nautobot nautobot-server check

docker compose --project-name lipford_nautobot_metrics `
  -f development/docker-compose.base.yml `
  -f development/docker-compose.redis.yml `
  -f development/docker-compose.postgres.yml `
  -f development/docker-compose.dev.yml `
  exec -T nautobot nautobot-server migrate --check

docker compose --project-name lipford_nautobot_metrics `
  -f development/docker-compose.base.yml `
  -f development/docker-compose.redis.yml `
  -f development/docker-compose.postgres.yml `
  -f development/docker-compose.dev.yml `
  exec -T nautobot nautobot-server test lipford_nautobot_metrics.tests --verbosity 2
```

## Verification Status

The latest local verification completed:

- Ruff lint checks.
- Ruff format checks.
- Poetry package validation.
- Wheel and source distribution build.
- MkDocs strict build.
- Nautobot system checks.
- Nautobot migration checks.
- Docker-backed Nautobot app tests.
- Live API and dashboard smoke checks.

The implemented test suite currently covers model validation, uniqueness constraints, job dry-run behavior, idempotent sample generation, dashboard permissions, API permissions, token authentication, and invalid API payload handling.

## Project Structure

```text
lipford_nautobot_metrics/
  api/                  REST API serializers, views, and routes
  migrations/           Django migrations
  templates/            Nautobot UI templates
  tests/                App test suite
  choices.py            Metric type/status choices
  filters.py            FilterSets
  forms.py              Nautobot forms
  jobs.py               Nautobot Jobs
  models.py             MetricDefinition and MetricValue
  navigation.py         Nautobot menu registration
  services.py           Metric collection and summary logic
  tables.py             Nautobot tables
  views.py              UI views
```

## Release Notes

Release notes are maintained under `docs/admin/release_notes/`. Use Towncrier fragments in `changes/` for future feature, fix, dependency, security, documentation, and housekeeping changes.

## Contributing

Before opening a pull request, run the quality checks listed above and include any relevant screenshots, API payloads, or Nautobot job output in the PR description. Keep changes small, tested, and aligned with Nautobot app conventions.
