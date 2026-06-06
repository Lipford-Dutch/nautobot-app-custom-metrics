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

The `v0.1.0` release is the first published release and has no prior app version migration requirements.
