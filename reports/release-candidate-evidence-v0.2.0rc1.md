# Release Candidate Evidence: v0.2.0rc1

## Scope

`v0.2.0rc1` is the final Alpha release candidate for Lipford Nautobot Metrics.
It promotes the `v0.2.0a1` Alpha work after adding governance evidence,
security-disposition notes, bug-tracking process documentation, and v3.0
forecasting.

## Owner Approval

The repository owner granted blanket approval on 2026-06-16 for Alpha release
evidence, network-security disposition notes, and release-candidate governance
while dedicated QA, SRE, and CAB teams are not yet defined.

This approval is valid for Alpha and release-candidate evidence. It does not
remove the production requirement for real separation of duties before an
unattended production deployment.

## Implemented Candidate Capabilities

- Canonical 60-metric Python catalog
- Persistent `MetricDefinition` and `MetricValue` models
- Required observation provenance through `MetricValue.source`
- Dashboard, list, detail, create, update, and delete UI surfaces
- REST API endpoints for definitions, values, summary, and atomic ingestion
- GraphQL type registration
- Idempotent sample-data Job
- Native Nautobot JobResult and ObjectChange collectors
- Retention Job with dry-run support
- Composite indexes for common summary and source/time queries
- CI matrix for Python 3.14, PostgreSQL, MySQL, and Nautobot 3.1.x
- GitHub release assets with checksums and provenance attestation

## Remaining Production Conditions

- Dedicated QA/SRE/CAB GitHub teams must replace named-maintainer fallback
  approvals.
- PyJWT advisories must be fixed through upstream Nautobot dependencies or
  formally accepted for the target production date.
- Upgrade, rollback, backup, restore, and load-test exercises must be executed
  in staging or a production-like lab.
- Collector schedules, retention settings, and operational ownership must be
  approved for the target deployment.

## Validation Evidence

The candidate branch must pass:

- `ruff check`
- `ruff format --check`
- `yamllint`
- `pymarkdownlnt`
- `mkdocs build --strict`
- `python -m compileall`
- GitHub Actions CI, including Docker and Nautobot test matrix
- GitHub Release workflow package build, wheel install/import, checksums, and
  provenance attestation

## Go/No-Go Decision

Go for Alpha release-candidate publication when all repository checks pass and
no `priority: p0` bugs are open.

No-go for production deployment until the remaining production conditions are
closed or formally accepted in a production change record.

