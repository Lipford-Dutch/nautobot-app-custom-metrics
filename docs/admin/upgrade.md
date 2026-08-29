# Upgrading the App

Use this guide when upgrading Lipford Nautobot Metrics in an existing Nautobot environment.

## Upgrade Guide

1. Review the release notes for compatibility or migration notes.
2. Back up the Nautobot database.
3. Upgrade the package in the Nautobot environment:

    ```shell
    pip install --upgrade lipford-nautobot-metrics
    ```

4. Run Nautobot post-upgrade tasks:

    ```shell
    nautobot-server post_upgrade
    ```

5. Restart Nautobot services, workers, and schedulers.
6. Confirm the app loads under Installed Apps and that `/plugins/lipford-nautobot-metrics/` renders.

The `v1.0.0` release has no new Django schema migration. Upgrading from the
`v0.2.0rc1` package registers the production UI integrations, Jobs, runtime
configuration, validators, and app metrics during `post_upgrade` and service
restart.
