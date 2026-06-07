"""DiffSync models for cellular reconciliation."""

from diffsync import DiffSyncModel


class RouterModel(DiffSyncModel):
    """Normalized router representation shared by source and target adapters."""

    _modelname = "router"
    _identifiers = ("serial_number",)
    _attributes = (
        "imei",
        "interface_name",
        "desired_iccid",
        "observed_iccid",
        "provisioning_state",
    )

    serial_number: str
    imei: str
    interface_name: str
    desired_iccid: str | None = None
    observed_iccid: str | None = None
    provisioning_state: str
