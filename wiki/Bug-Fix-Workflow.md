# Bug Fix Workflow

All defects discovered during v3 development, release-candidate validation, or
production-like testing must be tracked in GitHub.

## Required Labels

- `type: bug`
- `realm: bugfix`
- `status: triage`
- `priority: p0`, `priority: p1`, `priority: p2`, or `priority: p3`
- `release: candidate` when found against a release candidate

## Process

1. Open a bug report with environment, reproduction steps, observed behavior,
   expected behavior, and evidence.
2. Triage severity and release impact.
3. Create a `bugfix/<short-description>` branch.
4. Add or update regression tests.
5. Add a Towncrier fragment under `changes/<issue>.fixed`.
6. Merge only after required CI passes.

Open `priority: p0` bugs block release promotion.

