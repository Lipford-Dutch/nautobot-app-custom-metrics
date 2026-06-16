# Bug Triage and Fix Tracking

Use this process for defects found during Alpha, release-candidate, staging, or
production validation. Bugs must be tracked in GitHub before code changes are
merged unless the fix is required to restore a broken release workflow.

## Labels

| Label | Purpose |
| --- | --- |
| `type: bug` | Reproducible defect in released or candidate behavior. |
| `realm: bugfix` | Work is tracked through the bug-fix lane. |
| `status: triage` | Issue needs reproduction, severity, owner, or scope. |
| `priority: p0` | Release blocker or production outage. |
| `priority: p1` | Should fix before the next candidate unless accepted. |
| `priority: p2` | Important but not release blocking. |
| `priority: p3` | Low-risk cleanup or follow-up. |
| `release: candidate` | Found against the current release candidate. |

## Required Bug Report Evidence

Every bug report should include:

- Nautobot, Python, app, database, and deployment versions
- Expected behavior
- Observed behavior
- Reproduction steps
- Logs, tracebacks, API payloads, screenshots, or Job result references
- Impacted workflow, API endpoint, Job, collector, or model
- Whether the bug blocks the current release candidate

## Triage Flow

1. Apply `type: bug`, `realm: bugfix`, and `status: triage`.
2. Reproduce the issue in local Docker, GitHub Actions, or a staging lab.
3. Assign severity:
    - `priority: p0` blocks release or risks data loss/security exposure.
    - `priority: p1` affects core install, migration, UI, API, Job, or collector
      behavior.
    - `priority: p2` affects noncritical workflows or documentation.
    - `priority: p3` is minor cleanup.
4. Link the bug to the release candidate or milestone.
5. Create a `bugfix/<short-description>` branch.
6. Add or update regression tests before merging the fix.
7. Add a Towncrier fragment under `changes/<issue>.fixed`.

## Release Candidate Policy

A release candidate cannot be promoted when open `priority: p0` bugs exist.
Open `priority: p1` bugs require explicit owner acceptance in the release
evidence. `priority: p2` and `priority: p3` bugs may be deferred when they are
documented and do not invalidate the published release scope.
