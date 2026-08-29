# Production v1.0 Release Notes

## [v1.0.0] - 2026-08-29

Production v1.0.0 promotes the validated 60-metric platform from release
candidate to stable operation on Nautobot 3.

### Added

- Added database-backed runtime configuration for collector, ingestion, and
  retention settings.
- Added custom validation for structured metric context labels.
- Added Metrics home-page content, contextual safety banners, reusable Jinja
  formatting, and bounded-cardinality Prometheus app metrics.
- Added three registered Nautobot Jobs for sample data, native reference
  collection, and retention.

### Changed

- Corrected Nautobot 3 integration paths for navigation, Jobs, and GraphQL
  types so each feature is registered and visible in Installed Apps.
- Promoted the package version and documentation from `v0.2.0rc1` to stable
  `v1.0.0`.

### Validation

- Passed 61 combined application tests from the exact production wheels.
- Passed Nautobot system, migration, dependency, service, HTTPS, UI, API,
  Celery, rollback, and backup checks on the production Hostinger deployment.
