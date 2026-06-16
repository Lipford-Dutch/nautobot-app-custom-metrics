# GitHub Deployment Environments

This repository defines GitHub Actions deployment environments as Terraform in
`infrastructure/github-environments/`.

## Development

- Purpose: continuous integration and early test deployments.
- Allowed refs: `develop`, `feature/*`, `bugfix/*`.
- Review gate: none.
- Wait timer: none.
- Secrets: development-only `AWS_ROLE_ARN`.

## Staging

- Purpose: pre-production validation and integration testing.
- Allowed refs: `main`, `release/*`.
- Review gate: QA leads team, or a named maintainer until dedicated teams
  exist.
- Wait timer: none.
- Secrets: staging-only `AWS_ROLE_ARN` and staging external service token.

## Production

- Purpose: live customer-facing workloads.
- Allowed refs: `main`, `v*.*.*` tags.
- Review gate: SRE approvers and CAB teams, or a named maintainer until
  dedicated teams exist.
- Wait timer: 10 minutes.
- Secrets: production-only `AWS_ROLE_ARN` and production external service token.

## Security Controls

- Environments use explicit branch and tag deployment policies.
- Admin bypass is disabled.
- Self-review is disabled for staging and production.
- Secrets are environment scoped and intentionally not shared.
- Production releases should target immutable semantic-version tags whenever
  possible.

## Current Organizational Blocker

The target repository can enforce environment review, self-review prevention,
branch policies, and wait timers. True multi-party staging and production
review still requires organization teams for QA, SRE, and CAB ownership. Until
those teams exist, a named maintainer can validate the workflow mechanics, but
that is not equivalent to production-grade separation of duties.

The repository owner granted blanket approval on 2026-06-16 to use the
named-maintainer fallback for Alpha release-candidate evidence. Replace this
fallback with actual QA, SRE, and CAB teams before production deployment.
