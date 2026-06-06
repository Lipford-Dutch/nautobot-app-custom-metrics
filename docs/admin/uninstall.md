# Uninstall the App from Nautobot

Use this guide to remove Lipford Nautobot Metrics from a Nautobot environment.

## Database Cleanup

Prior to removing the app from the `nautobot_config.py`, run the following command to roll back any migration specific to this app.

```shell
nautobot-server migrate lipford_nautobot_metrics zero
```

This removes the app-owned database tables, including metric definitions and values. Export any data that must be retained before running the migration rollback.

## Remove App configuration

Remove the configuration you added in `nautobot_config.py` from `PLUGINS` and `PLUGINS_CONFIG`.

## Uninstall the package

```shell
pip uninstall lipford-nautobot-metrics
```
