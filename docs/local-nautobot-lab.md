# Local Nautobot Lab — Validated Reproduction Guide

This document captures the **verified** steps to stand up a local Nautobot lab
with the `lipford_nautobot_metrics` app installed, migrated, seeded, and
testable. It complements the cookiecutter
[`docs/dev/dev_environment.md`](dev/dev_environment.md) with a concise,
command-by-command path that has been run end-to-end against this repository.

## Verified stack

| Component | Version (validated) |
|-----------|---------------------|
| Nautobot  | 3.1.3 |
| Django    | 5.2.15 |
| Python    | 3.12.13 (container) |
| Database  | PostgreSQL 17 (alpine) |
| Cache/Queue | Redis 6 (alpine) |
| App package | `lipford_nautobot_metrics` |
| App `PLUGINS` name | `lipford_nautobot_metrics` |
| Web UI    | http://localhost:8080 |
| Docs site | http://localhost:8001 |

> The app declares support for Python 3.10–3.14 and Nautobot `>=3.1.0,<4.0.0`.
> The lab pins Python 3.12 via `PYTHON_VER` for a known-good Nautobot 3.1.3
> image. See [Compatibility notes](#compatibility-notes) for Python 3.14.

## Prerequisites

- Docker Engine + Docker Compose v2
- `invoke` and `poetry` on the host **only if** you use the `invoke` task
  wrappers. All steps below also work with raw `docker` commands.

## Quick start (invoke workflow)

```bash
# 1. Create the local credentials file (dummy values, never committed)
cp development/creds.example.env development/creds.env

# 2. Build the image (uses NAUTOBOT_VER / PYTHON_VER from invoke.yml or env)
invoke build

# 3. Start the full stack (nautobot, worker, beat, db, redis, docs)
invoke start

# 4. Apply migrations and run post_upgrade
invoke migrate
invoke post-upgrade        # or: invoke cli -c "nautobot-server post_upgrade"

# 5. Create the local superuser (admin / admin from creds.env)
invoke createsuperuser

# 6. Seed deterministic sample metrics (idempotent)
invoke cli -c "echo 'from lipford_nautobot_metrics.services import seed_sample_metrics; print(seed_sample_metrics(sample_days=3))' | nautobot-server shell"

# 7. Run the test suite
invoke tests            # lint + unit tests
# or just unit tests:
invoke unittest
```

Open http://localhost:8080 and log in as `admin` / `admin`.
The app appears under the **Metrics** navigation tab.

## Quick start (raw docker — no invoke required)

These are the exact commands used to validate this lab.

```bash
# Build + start
cp development/creds.example.env development/creds.env
docker compose -f development/docker-compose.base.yml \
               -f development/docker-compose.dev.yml \
               -f development/docker-compose.postgres.yml \
               -f development/docker-compose.redis.yml up -d

C=lipford-nautobot-metrics-nautobot-1

# Migrate + post_upgrade
docker exec $C nautobot-server migrate
docker exec $C nautobot-server post_upgrade

# Seed sample data (idempotent — safe to re-run)
printf '%s\n' \
  "from lipford_nautobot_metrics.services import seed_sample_metrics" \
  "print(seed_sample_metrics(sample_days=3))" | docker exec -i $C nautobot-server shell

# Run tests (creates/destroys an isolated test DB)
docker exec $C nautobot-server test lipford_nautobot_metrics --verbosity 2
```

> **Windows / Git Bash note:** prefix `docker exec -w <path>` and any
> container-absolute paths with `export MSYS_NO_PATHCONV=1` to stop Git Bash
> from rewriting `/source` into `C:/Program Files/Git/source`.

## Smoke checks (all verified green)

```bash
C=lipford-nautobot-metrics-nautobot-1
T=0123456789abcdef0123456789abcdef01234567   # dev token from creds.example.env

# Core
docker exec $C nautobot-server check                       # -> 0 issues
docker exec $C nautobot-server makemigrations lipford_nautobot_metrics --check --dry-run  # -> No changes

# App import + ORM
printf '%s\n' \
  "import lipford_nautobot_metrics as m; print(m.__version__)" \
  "from lipford_nautobot_metrics.models import MetricDefinition, MetricValue" \
  "print(MetricDefinition.objects.count(), MetricValue.objects.count())" \
  | docker exec -i $C nautobot-server shell

# HTTP
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/login/                     # 200
curl -s -H "Authorization: Token $T" http://localhost:8080/api/plugins/lipford-nautobot-metrics/metric-definitions/   # JSON
curl -s -H "Authorization: Token $T" http://localhost:8080/api/plugins/lipford-nautobot-metrics/summary/             # JSON
```

## App surface reference

| Surface | Location |
|---------|----------|
| Models | `MetricDefinition`, `MetricValue` (`models.py`) |
| Dashboard UI | `/plugins/lipford-nautobot-metrics/` |
| Model list/detail UI | `metric-definitions/`, `metric-values/` (NautobotUIViewSet) |
| REST API | `/api/plugins/lipford-nautobot-metrics/{metric-definitions,metric-values,summary}/` |
| Job | `Seed sample metric data` (grouping: *Lipford Nautobot Metrics*) |
| Navigation | **Metrics** tab → *Custom Metrics* group |
| Permissions | `view_metricdefinition`, `view_metricvalue`, `add_*` |

## Stopping / resetting

```bash
invoke stop                 # stop containers, keep data
invoke destroy              # stop + remove volumes (full reset)
# raw:
docker compose -f development/docker-compose.base.yml -f development/docker-compose.dev.yml \
  -f development/docker-compose.postgres.yml -f development/docker-compose.redis.yml down -v
```

## Compatibility notes

- **Nautobot version:** Validated on 3.1.3. The app pins `>=3.1.0,<4.0.0`; no
  legacy Nautobot 1.x / 2.x APIs are used. It is built natively against the
  modern `nautobot.apps` API surface (`NautobotAppConfig`, `NautobotUIViewSet`,
  `register_jobs`, `extras_features`).
- **Python 3.14:** Declared as supported in `pyproject.toml`
  (`python = ">=3.10,<3.15"`). The lab image runs Python 3.12 because that is
  the version with a known-good published Nautobot 3.1.3 image. Running the
  container on 3.14 is **not yet proven** here — build with
  `PYTHON_VER=3.14 invoke build` and re-run the test suite before relying on it.
  No application code change is required for 3.14; the gate is upstream
  Nautobot/dependency wheel availability for 3.14, not this app.
- **No external integrations:** The app runs entirely inside Nautobot. It does
  not call any external Nautobot instance, network device, or cloud API, so no
  real secrets or network egress are required for the lab.
</content>
