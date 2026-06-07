"""Vendor-side DiffSync adapter and collector contract."""

from collections.abc import Iterable
from typing import Protocol

from diffsync import Adapter

from nautobot_cellular_sot.schemas import NormalizedCellularRouter
from nautobot_cellular_sot.ssot.models import RouterModel


class CellularCollector(Protocol):
    """Contract implemented by Cisco, Cradlepoint, Sierra, and other collectors."""

    def collect(self) -> Iterable[NormalizedCellularRouter]:
        """Return normalized cellular records."""


class VendorAdapter(Adapter):
    """Read-only DiffSync adapter backed by a normalized external collector."""

    top_level = ["router"]
    router = RouterModel

    def __init__(self, *args, collector: CellularCollector, **kwargs):
        """Initialize the adapter with an explicit collector dependency."""
        super().__init__(*args, **kwargs)
        self.collector = collector

    def load(self):
        """Load normalized vendor records and reject duplicate identifiers."""
        seen_serials: set[str] = set()
        seen_imeis: set[str] = set()
        for payload in self.collector.collect():
            if payload.serial_number in seen_serials:
                raise ValueError(f"Duplicate vendor serial number: {payload.serial_number}")
            if payload.imei in seen_imeis:
                raise ValueError(f"Duplicate vendor IMEI: {payload.imei}")
            seen_serials.add(payload.serial_number)
            seen_imeis.add(payload.imei)
            self.add(
                RouterModel(
                    serial_number=payload.serial_number,
                    imei=payload.imei,
                    interface_name=payload.interface_name,
                    observed_iccid=payload.iccid,
                    provisioning_state="active",
                )
            )
