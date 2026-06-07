# v0.1 Release Notes

This document describes all new features and changes in the `0.1` release series. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] - 2026-06-05

### Added

- Added the initial Lipford Nautobot Metrics app for Nautobot `>=3.1.0,<4.0.0`.
- Added `MetricDefinition` and `MetricValue` models with Nautobot UI, filters, forms, tables, REST API endpoints, permissions, custom fields, tags, webhooks, export templates, and GraphQL support.
- Added the v1 first-batch ROI metrics from Section 2.1 of the metrics definition guide:
    - Time Saved per Automated Task
    - Reduction in Manual Error Rates
    - Increased Task Throughput
    - Automation Adoption Rate
- Added a dashboard at `/plugins/lipford-nautobot-metrics/`.
- Added a summary API endpoint at `/api/plugins/lipford-nautobot-metrics/summary/`.
- Added the `Seed sample metric data` Nautobot Job for idempotent sample observations.
- Added app configuration schema and defaults for sample metric data generation.
- Added documentation, security policy, Dependabot configuration, issue templates, and release handoff notes.
- Added the initial `nautobot_cellular_sot` app package with carrier profiles, cellular routers, SIM cards, latest-only operational snapshots, dashboard, REST API, GraphQL, Device detail panel, and SSoT adapter scaffolding.

### Changed

- Replaced generated cookiecutter placeholder metadata with project-specific README, release, and repository metadata.

### Security

- Performed a release dependency audit with `pip-audit==2.10.0`.
- Documented the remaining upstream-constrained `PyJWT==2.12.1` advisory inherited through the Nautobot authentication dependency chain.
