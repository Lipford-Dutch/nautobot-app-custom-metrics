# Codex Session Handoff: Lipford Nautobot Metrics

## Repository

- Local path: `C:\Users\spamw\Documents\Lipford Nautobot Metrics`
- GitHub repository: `Lipford-Dutch/nautobot-app-custom-metrics`
- Stable branch: `main`
- Release branch: `release/1.0.0-production`
- Current package: `1.0.0`
- Previous published prerelease: `v0.2.0rc1`

## Current State

Lipford Nautobot Metrics is a Nautobot 3.1 app with a full 60-metric catalog,
persistent metric storage, UI, REST API, GraphQL registration, sample data,
bulk ingestion, native Nautobot reference collectors, retention controls,
CI/CD, release provenance, and repository governance.

The owner approved Production v1.0.0 promotion on August 29, 2026 after
acceptance testing passed. The production deployment, rollback behavior,
services, TLS, Jobs, metrics, APIs, UI, and backup were verified on Nautobot
3.2.2.

## Implemented Functionality

- Canonical 60-metric catalog in `lipford_nautobot_metrics/catalog.py`
- `MetricDefinition` and `MetricValue` Nautobot models
- Required observation provenance with `MetricValue.source`
- Dashboard and Nautobot CRUD views
- REST API:
    - `/api/plugins/lipford-nautobot-metrics/metric-definitions/`
    - `/api/plugins/lipford-nautobot-metrics/metric-values/`
    - `/api/plugins/lipford-nautobot-metrics/summary/`
    - `/api/plugins/lipford-nautobot-metrics/ingest/`
- GraphQL type registration
- Nautobot Jobs:
    - `Seed sample metric data`
    - `Collect Nautobot reference metrics`
    - `Purge retained metric values`
- App configuration:
    - `sample_metric_days`
    - `sample_metric_source`
    - `collector_lookback_minutes`
    - `max_ingest_batch_size`
    - `retention_days`
- GitHub environments, branch protections, release workflow, CodeQL,
  dependency review, Scorecard, and coverage checks
- Bug-fix tracking process and labels for release-candidate defects

## Important Artifacts

- Release evidence: `reports/release-candidate-evidence-v0.2.0rc1.md`
- Session export: `reports/session-details-export-2026-06-16-v0.2.0rc1.md`
- Production readiness: `docs/admin/production_readiness.md`
- Security advisory disposition: `docs/admin/security_advisories.md`
- Bug triage: `docs/dev/bug_triage.md`
- V2 planning: `docs/admin/v2_planning.md`
- Release notes: `docs/admin/release_notes/version_1.0.md`

## Validation Commands

Local validation:

```powershell
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\yamllint.exe .
.\.venv\Scripts\pymarkdownlnt.exe scan README.md docs reports
.\.venv\Scripts\mkdocs.exe build --strict
.\.venv\Scripts\python.exe -m compileall lipford_nautobot_metrics
```

Nautobot validation inside a Linux/Docker Nautobot environment:

```shell
python -c "import lipford_nautobot_metrics"
nautobot-server check
nautobot-server makemigrations lipford_nautobot_metrics --check --dry-run
nautobot-server migrate --noinput
nautobot-server post_upgrade
nautobot-server collectstatic --noinput
nautobot-server test lipford_nautobot_metrics
```

GitHub Actions remains the authoritative Docker/Linux validation path for this
Windows workstation.

## V2 Follow-Up

- Complete the v2 specification and planning package by October 1, 2026.
- Target v2 delivery for end of 2026.
- Revisit the upstream-constrained dependency exception and expanded scale
  targets during that review.

## Next Suggested Work

1. Merge the Production v1.0.0 release PR after required checks and approval.
2. Publish the `v1.0.0` GitHub release named **Production** with wheel and sdist.
3. Begin v2 specification work before the October 1, 2026 checkpoint.
