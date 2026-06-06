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
- Review gate: QA leads team.
- Wait timer: none.
- Secrets: staging-only `AWS_ROLE_ARN` and staging external service token.

## Production

- Purpose: live customer-facing workloads.
- Allowed refs: `main`, `v*.*.*` tags.
- Review gate: SRE approvers and CAB teams.
- Wait timer: 10 minutes.
- Secrets: production-only `AWS_ROLE_ARN` and production external service token.

## Security Controls

- Environments use explicit branch and tag deployment policies.
- Admin bypass is disabled.
- Self-review is disabled for staging and production.
- Secrets are environment scoped and intentionally not shared.
- Production releases should target immutable semantic-version tags whenever
  possible.
