# Extending the App

Extending the application is welcome. Open an issue first for larger changes so the metric model, data-source assumptions, and dashboard impact can be reviewed before implementation.

## Adding a Metric

1. Add a stable key to `MetricKindChoices`.
2. Add a default entry in `DEFAULT_METRIC_DEFINITIONS`.
3. Add collection or sample data logic in `services.py` or a dedicated collector.
4. Add model, job, dashboard, and API tests.
5. Update user documentation and release notes.

Prefer additive changes. Do not modify Nautobot core models.
