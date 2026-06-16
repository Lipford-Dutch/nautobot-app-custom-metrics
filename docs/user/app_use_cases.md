# Using the App

## Saturated Metric Review

Use the dashboard to review every enabled metric across the full catalog:

- Latest observed value
- Average value
- Target value
- Sample count
- Latest timestamp
- Source label

The dashboard groups the 60 canonical metrics by ROI, business impact, user
activity, Golden Config, SSoT, Device Lifecycle Management, and Job execution.
After sample data is seeded, the saturation and observation coverage cards
should both show `60/60`.

## Sample Data Population

Run the `Seed sample metric data` Nautobot Job to create deterministic sample values for local validation or demonstrations. The job is idempotent, so repeated runs update existing observations for the same metric, timestamp, and source instead of creating duplicates.

The job supports dry-run mode to validate behavior without committing records.

## API Consumption

Use the summary endpoint for lightweight external dashboard consumers:

```shell
curl -H "Authorization: Token <token>" \
  https://nautobot.example.com/api/plugins/lipford-nautobot-metrics/summary/
```

Use the model endpoints when integrations need full CRUD behavior:

- `/api/plugins/lipford-nautobot-metrics/metric-definitions/`
- `/api/plugins/lipford-nautobot-metrics/metric-values/`
- `/api/plugins/lipford-nautobot-metrics/ingest/`

## Permissions

Users need the standard Nautobot model permissions for metric definitions and metric values. The dashboard and summary API require view permissions for both models.
