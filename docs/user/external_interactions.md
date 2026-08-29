# External Interactions

Lipford Nautobot Metrics stores metric definitions and values inside Nautobot.
The app does not require an external metrics database for the `v1.0.0`
release candidate.

## External System Integrations

### From the App to Other Systems

The app does not initiate outbound calls to external systems in `v1.0.0`.
Sample data is generated locally by the `Seed sample metric data` Nautobot Job.
Native Nautobot JobResult and ObjectChange data can be collected through the
`Collect Nautobot reference metrics` Job.

### From Other Systems to the App

External systems should write observations through the atomic bulk-ingestion
endpoint when authenticated and authorized. Direct model endpoints remain
available for administrative CRUD.

## Nautobot REST API endpoints

- `/api/plugins/lipford-nautobot-metrics/metric-definitions/`
- `/api/plugins/lipford-nautobot-metrics/metric-values/`
- `/api/plugins/lipford-nautobot-metrics/ingest/`
- `/api/plugins/lipford-nautobot-metrics/summary/`

Example:

```shell
curl -H "Authorization: Token ${NAUTOBOT_TOKEN}" \
  https://nautobot.example.com/api/plugins/lipford-nautobot-metrics/summary/
```
