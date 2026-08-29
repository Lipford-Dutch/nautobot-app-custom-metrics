# Production Readiness

Use this checklist when promoting Lipford Nautobot Metrics to a production
deployment. The checklist is intentionally evidence based: every
item must be backed by a command output, GitHub Actions run, release artifact,
or signed operational note.

## Current Production Status

`v1.0.0` is the production release candidate. It passed owner acceptance
testing and a verified Nautobot 3.2.3 deployment on August 29, 2026. Final
release publication follows the protected pull-request and tag workflow.

## Production Approval

The repository owner approved preparation of Production v1.0.0 on August 29,
2026 after application testing passed. The dependency lock was refreshed to
fixed releases, including Nautobot 3.2.3, Django 5.2.17, sqlparse 0.6.0,
cryptography 50.0.1, GitPython 3.1.61, Pillow 12.3.0, and PyJWT 2.13.0.

## Required Gates

| Gate | Required Evidence | Status |
| --- | --- | --- |
| Fresh install | Wheel installs into a clean Nautobot environment and the app imports. | Complete for `v1.0.0`. |
| Upgrade | Previous release upgrades without data loss. | Complete on the Hostinger promotion deployment. |
| Rollback | Prior package restoration is tested and documented. | Complete; deployment rollback was exercised twice before final promotion. |
| Migration safety | Schema check and post-upgrade migration complete without pending migrations. | Complete. |
| Retention | Retention remains operator-controlled with dry-run support. | Complete with production default disabled. |
| Bulk ingestion | Authenticated ingestion handles validation errors atomically. | Complete. |
| Collectors | JobResult and ObjectChange collectors are idempotent and registered as Jobs. | Complete. |
| Performance | Production alpha dataset and bounded aggregate paths pass smoke checks. | Accepted for v1 scope; expanded targets due in v2 planning. |
| Security | HTTPS, secure cookies, firewall, telemetry policy, and advisory disposition are documented. | Complete; the production dependency lock uses fixed releases. |
| Operations | Backup, restore, rollback, service, worker, and scheduler procedures are exercised. | Complete. |

## Validation Commands

Run these commands against a production-like staging deployment before a
production release.

```shell
poetry run ruff check .
poetry run ruff format --check .
poetry run yamllint .
poetry run markdownlint-cli2 README.md "docs/**/*.md"
poetry run mkdocs build --strict
poetry build
```

Inside the Nautobot container or virtual environment:

```shell
python -c "import lipford_nautobot_metrics"
nautobot-server check
nautobot-server makemigrations lipford_nautobot_metrics --check --dry-run
nautobot-server migrate --noinput
nautobot-server post_upgrade
nautobot-server collectstatic --noinput
nautobot-server test lipford_nautobot_metrics
```

For Docker-based validation:

```shell
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
```

## Upgrade Exercise

1. Restore or create a staging database on the previous released version.
2. Record pre-upgrade counts:

    ```shell
    nautobot-server shell -c "from lipford_nautobot_metrics.models import MetricDefinition, MetricValue; print(MetricDefinition.objects.count(), MetricValue.objects.count())"
    ```

3. Install the candidate wheel.
4. Run `nautobot-server post_upgrade`.
5. Re-run the count check and compare the summary API output.
6. Run the sample-data Job in dry-run mode, then normal mode.
7. Run the native collector Job in dry-run mode.
8. Confirm the UI list, detail, summary API, and GraphQL query render without
   server errors.

## Rollback Exercise

Rollback must be practiced in staging before production. If a migration cannot
be safely reversed in place, the supported rollback path is:

1. Stop Nautobot web, worker, beat, and scheduler services.
2. Restore the pre-upgrade database backup.
3. Reinstall the previous approved wheel.
4. Run `nautobot-server post_upgrade`.
5. Start services and run smoke checks.

Do not run retention jobs during an upgrade or rollback window.

## Production Go/No-Go

Production promotion is a no-go when any of the following are true:

- Docker or staging validation is unavailable.
- Required branch checks are failing or bypassed.
- GitHub environment reviewers are placeholders or single-person substitutes.
- Secret scanning or push protection is disabled.
- Dependency advisories lack either a fix or an approved exception.
- Migration, backup, restore, and rollback evidence is missing.
- Collector schedule and retention settings are not documented for the target
  deployment.
