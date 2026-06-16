# Operations Runbook

Use this runbook for release-candidate and production-like validation.

## Standard Checks

```shell
nautobot-server check
nautobot-server makemigrations lipford_nautobot_metrics --check --dry-run
nautobot-server migrate --noinput
nautobot-server post_upgrade
nautobot-server collectstatic --noinput
nautobot-server test lipford_nautobot_metrics
```

## Release Candidate Validation

1. Install the candidate wheel.
2. Enable `lipford_nautobot_metrics`.
3. Run migrations and `post_upgrade`.
4. Run the sample metric Job.
5. Run reference collectors in dry-run mode.
6. Validate UI, REST API, GraphQL, and summary endpoint.
7. Confirm no open `priority: p0` bugs exist.

## Production Go/No-Go

Production is no-go when:

- Required checks are failing.
- Upgrade or rollback evidence is missing.
- Backup/restore was not rehearsed.
- PyJWT advisory disposition is missing.
- GitHub environment reviewers are placeholders.
- Retention and collector schedules are not approved.

