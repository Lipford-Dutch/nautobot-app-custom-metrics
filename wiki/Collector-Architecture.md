# Collector Architecture

v3.0 introduces a pluggable collector model for optional Nautobot app
integrations and richer first-party Nautobot signals.

## Principles

- No hard import dependency on optional apps.
- Every collector supports dry-run.
- Every observation includes source provenance.
- Collection windows are bounded and idempotent.
- Failures include source, window, and count context.
- Sensitive identifiers are not logged.

## Candidate Collectors

| Collector | Source | Status |
| --- | --- | --- |
| JobResult | Nautobot core | Live baseline |
| ObjectChange | Nautobot core | Live baseline |
| Golden Config | Optional app | v3.0 planned |
| SSoT | Optional app | v3.0 planned |
| Device Lifecycle Management | Optional app | v3.0 planned |
| User activity | Nautobot auth/session/audit data | v3.0 planned |

## Acceptance Criteria

- Registry-driven collector discovery
- Idempotent collection by metric, timestamp, and source
- Permission-safe execution
- Tests for optional app absence
- Tests for partial failure and retry behavior

