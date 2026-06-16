# Codex Session Handoff: Lipford Nautobot Metrics

## Repository

- Local path: `C:\Users\spamw\Documents\Lipford Nautobot Metrics`
- GitHub repository: `Lipford-Dutch/nautobot-app-custom-metrics`
- Active development branch: `develop`
- Current working branch: `codex/final-alpha-rc-evidence`
- Current package candidate: `0.2.0rc1`
- Previous published prerelease: `v0.2.0a1`

## Current State

Lipford Nautobot Metrics is a Nautobot 3.1 app with a full 60-metric catalog,
persistent metric storage, UI, REST API, GraphQL registration, sample data,
bulk ingestion, native Nautobot reference collectors, retention controls,
CI/CD, release provenance, and repository governance.

The owner granted blanket approval on 2026-06-16 for Alpha and
release-candidate evidence while dedicated QA, SRE, and CAB teams are not yet
defined. This approval is documented for Alpha/RC release evidence and security
disposition. It is not a substitute for future production separation of duties.

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
- v3.0 forecast: `docs/dev/release_v3_forecast.md`
- Release notes: `docs/admin/release_notes/version_0.2.md`

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

## Remaining Production Conditions

- Replace named-maintainer fallback approvals with QA, SRE, and CAB GitHub
  teams.
- Resolve or formally accept upstream-constrained PyJWT advisories for the
  production target date.
- Complete staging upgrade, rollback, backup/restore, retention, and load-test
  exercises.
- Define production collector schedules, retention policy, and operational
  ownership.
- Decide whether and when to enable PyPI publishing.

## Next Suggested Work

1. Merge `codex/final-alpha-rc-evidence` after CI passes.
2. Tag and publish `v0.2.0rc1`.
3. Review the session export in `reports/`.
4. Convert v3.0 forecast features into GitHub issues or milestones.
5. Create QA, SRE, and CAB teams in the GitHub organization before production
   promotion.
