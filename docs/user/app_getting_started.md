# Getting Started with the App

## Install the App

Follow the [Installation Guide](../admin/install.md) to install and enable the app.

## First Workflow

1. Confirm the app appears on Nautobot's Installed Apps page.
2. Open Metrics > Custom Metrics > Dashboard.
3. Open Jobs and enable `Seed sample metric data` if it has not been enabled yet.
4. Run the job with the default `sample_days` value.
5. Open Metric Definitions and confirm all 60 canonical metric definitions exist.
6. Open Metric Values and confirm daily sample observations exist.
7. Open `/api/plugins/lipford-nautobot-metrics/summary/` with an authenticated API token to verify the summary endpoint.

## Next Steps

After the first workflow is verified, replace or extend the sample job with a real collector that writes production metric values from Nautobot job results, external automation platforms, change systems, or team-provided baseline data.
