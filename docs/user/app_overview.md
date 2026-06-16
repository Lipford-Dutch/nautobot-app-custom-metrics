# App Overview

Lipford Nautobot Metrics adds custom metric tracking to Nautobot. It stores metric definitions and timestamped metric values, exposes them through the Nautobot UI, REST API, GraphQL, and a dashboard for reviewing current values.

The current catalog contains 60 canonical metrics across:

- ROI and business impact
- User activity
- Golden Config
- SSoT
- Device Lifecycle Management
- Job execution

## Audience

This app is intended for Nautobot administrators, automation engineers, and operations leaders who need to quantify the business and operational impact of Nautobot-driven automation.

## Nautobot Features Used

The app uses standard Nautobot app patterns:

- Primary models for `MetricDefinition` and `MetricValue`
- Nautobot UI viewsets, tables, forms, filters, and navigation
- REST API endpoints under `/api/plugins/lipford-nautobot-metrics/`
- A summary API endpoint for dashboard consumers
- Nautobot Jobs for sample metric data, reference collection, and retention
- Authenticated bulk-ingestion endpoint
- Permissions, tags, custom fields, webhooks, custom links, export templates, and GraphQL support

## Current Views

- Dashboard: `/plugins/lipford-nautobot-metrics/`
- Metric Definitions: `/plugins/lipford-nautobot-metrics/metric-definitions/`
- Metric Values: `/plugins/lipford-nautobot-metrics/metric-values/`
