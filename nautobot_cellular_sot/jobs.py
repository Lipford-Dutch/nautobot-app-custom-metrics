"""Nautobot Jobs for cellular reconciliation and external polling triggers."""

from nautobot.apps.jobs import BooleanVar, Job, register_jobs


class ReconcileCellularInventory(Job):
    """Reconcile a normalized collector snapshot against Nautobot desired state."""

    dryrun = BooleanVar(default=True, description="Calculate and log differences without changing Nautobot.")

    class Meta:
        """Job metadata."""

        name = "Reconcile cellular inventory"
        description = "Compare normalized vendor cellular inventory with Nautobot desired state."
        has_sensitive_variables = False

    def run(self, dryrun=True):
        """Validate configuration and direct operators to the configured SSoT integration."""
        mode = "dry-run" if dryrun else "apply"
        self.logger.info("Cellular reconciliation requested in %s mode.", mode)
        self.logger.warning(
            "No vendor collector is configured in the base app. Register a vendor-specific collector before applying changes."
        )
        return f"Cellular reconciliation requested in {mode} mode; no vendor collector configured."


register_jobs(ReconcileCellularInventory)
