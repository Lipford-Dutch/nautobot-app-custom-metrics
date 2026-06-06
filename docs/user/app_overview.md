# App Overview

Lipford Nautobot Metrics adds custom metric tracking to Nautobot. It stores metric definitions and timestamped metric values, exposes them through the Nautobot UI and REST API, and provides a simple dashboard for reviewing current values.

The v1 first-batch metrics are ROI-focused:

- Time Saved per Automated Task
- Reduction in Manual Error Rates
- Increased Task Throughput
- Automation Adoption Rate

These are intentionally small starting points so the app can be verified end to end before expanding into additional metric categories.

## Audience

This app is intended for Nautobot administrators, automation engineers, and operations leaders who need to quantify the business and operational impact of Nautobot-driven automation.

## Nautobot Features Used

The app uses standard Nautobot app patterns:

- Primary models for `MetricDefinition` and `MetricValue`
- Nautobot UI viewsets, tables, forms, filters, and navigation
- REST API endpoints under `/api/plugins/lipford-nautobot-metrics/`
- A summary API endpoint for dashboard consumers
- A Nautobot Job for sample metric data population
- Permissions, tags, custom fields, webhooks, custom links, export templates, and GraphQL support

## Current Views

- Dashboard: `/plugins/lipford-nautobot-metrics/`
- Metric Definitions: `/plugins/lipford-nautobot-metrics/metric-definitions/`
- Metric Values: `/plugins/lipford-nautobot-metrics/metric-values/`
