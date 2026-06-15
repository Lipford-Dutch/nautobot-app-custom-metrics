# Production Readiness

Use this checklist before promoting Lipford Nautobot Metrics beyond an Alpha
or staging deployment. The checklist is intentionally evidence based: every
item must be backed by a command output, GitHub Actions run, release artifact,
or signed operational note.

## Current Production Status

`v0.2.0a1` is an Alpha prerelease. It is suitable for internal testing and
moderate-volume validation, but it is not approved for unattended production
operation until the required production gates in this document are complete.

## Required Gates

| Gate | Required Evidence | Status |
| --- | --- | --- |
| Fresh install | Wheel installs into a clean Nautobot 3.1 environment and the app imports. | Complete for `v0.2.0a1` release workflow. |
| Upgrade | Previous release upgrades to the candidate without data loss. | Required before production. |
| Rollback | Candidate rollback path is tested and documented. | Required before production. |
| Migration safety | Fresh, forward, rollback, and re-apply migration paths are tested. | Partial. |
| Retention | Dry-run and destructive retention runs are validated against backed-up data. | Partial. |
| Bulk ingestion | Authenticated ingestion handles validation errors atomically. | Complete for Alpha; production volume test required. |
| Collectors | JobResult and ObjectChange collectors are idempotent and scheduled safely. | Complete for Alpha; production schedule test required. |
| Performance | Summary, list, and ingest paths meet the agreed production data-volume target. | Required before production. |
| Security | Branch protection, environment gates, secret scanning, and advisory disposition are complete. | Partial. |
| Operations | Backup, restore, rollback, incident, and collector runbooks are exercised. | Required before production. |

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

