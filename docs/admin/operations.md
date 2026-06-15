# Operations

## Data Ownership

The Python catalog owns each definition's key, name, category, kind, unit,
description, and formula. Operators own baseline, target, and enabled values.
Catalog synchronization repairs catalog metadata without overwriting
operator-controlled fields.

Nautobot is the authoritative store for moderate-volume metric observations.
Every observation requires provenance in `source`. The stable observation
identity is metric definition, timestamp, and source.

## Collection

The **Collect Nautobot reference metrics** Job aggregates completed JobResult
and ObjectChange records over a configurable lookback window. Repeating a run
for the same minute and window updates the existing observations.

Schedule collection only after the sample Job has created the canonical
definitions. Collector failures leave prior observations intact and are
visible in Nautobot Job logs.

## Retention

`retention_days` defaults to `0`, which disables automatic retention.
Operators can run **Purge retained metric values** in dry-run mode before
deleting observations. Back up the Nautobot database before changing the
retention policy.

## Backup, Restore, and Rollback

Metric definitions and observations are stored in the Nautobot database and
follow the deployment's existing backup and restore process. Before an app
upgrade:

1. Back up the database.
2. Build and retain the previous app wheel.
3. Run migrations and smoke tests in staging.
4. Confirm observation counts and summary API output.

For rollback, restore the prior wheel and database backup when a migration
cannot be safely reversed. Never run retention during an upgrade or rollback
window.

## Failure Signals

- Failed collector or retention Jobs in Nautobot Job Results
- Missing recent observations for collector sources
- Bulk-ingestion HTTP 400 or 403 responses
- Increasing summary API latency
- Unexpected observation growth
