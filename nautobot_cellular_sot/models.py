"""Database models for Nautobot Cellular SoT."""

from django.core.exceptions import ValidationError
from django.db import models
from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models.generics import PrimaryModel
from nautobot.dcim.models import Device, Interface, InventoryItem
from nautobot.extras.utils import extras_features

from nautobot_cellular_sot.choices import (
    CarrierAuthenticationChoices,
    ProvisioningStateChoices,
    RegistrationStateChoices,
    SIMSlotChoices,
)


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class CarrierProfile(PrimaryModel):
    """Reusable desired-state cellular carrier and APN configuration."""

    natural_key_field_names = ["name"]

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    carrier_name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, db_index=True)
    apn = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    authentication_type = models.CharField(
        max_length=32,
        choices=CarrierAuthenticationChoices,
        default="none",
    )
    roaming_allowed = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)

    class Meta:
        """Model options."""

        ordering = ["carrier_name", "name"]
        verbose_name = "Carrier Profile"
        verbose_name_plural = "Carrier Profiles"

    def __str__(self):
        """Return the display name."""
        return f"{self.name} ({self.carrier_name})"


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class CellularRouter(PrimaryModel):
    """Cellular-specific desired state bound to a Nautobot Device."""

    natural_key_field_names = ["device__name"]

    device = models.OneToOneField(
        to=Device,
        on_delete=models.PROTECT,
        related_name="cellular_router",
    )
    modem_interface = models.OneToOneField(
        to=Interface,
        on_delete=models.PROTECT,
        related_name="cellular_router",
    )
    modem_inventory_item = models.OneToOneField(
        to=InventoryItem,
        on_delete=models.PROTECT,
        related_name="cellular_router",
        blank=True,
        null=True,
    )
    imei = models.CharField(max_length=15, unique=True, db_index=True)
    provisioning_state = models.CharField(
        max_length=32,
        choices=ProvisioningStateChoices,
        default="planned",
        db_index=True,
    )
    vendor_platform = models.CharField(max_length=64, blank=True)
    external_system_id = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, db_index=True)
    last_reconciled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Model options."""

        ordering = ["device__name"]
        verbose_name = "Cellular Router"
        verbose_name_plural = "Cellular Routers"
        constraints = (
            models.UniqueConstraint(
                fields=("device", "modem_interface"),
                name="cellular_sot_unique_device_interface",
            ),
        )

    def __str__(self):
        """Return the device name."""
        return str(self.device)

    def clean(self):
        """Validate router relationships and identifiers."""
        super().clean()
        if self.imei and (not self.imei.isdigit() or len(self.imei) != 15):
            raise ValidationError({"imei": "IMEI must contain exactly 15 digits."})
        if self.device_id and self.modem_interface_id and self.modem_interface.device_id != self.device_id:
            raise ValidationError({"modem_interface": "Modem interface must belong to the selected device."})
        if self.device_id and self.modem_inventory_item_id and self.modem_inventory_item.device_id != self.device_id:
            raise ValidationError({"modem_inventory_item": "Inventory item must belong to the selected device."})


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class SIMCard(PrimaryModel):
    """Physical SIM or eSIM profile assigned to a cellular router."""

    natural_key_field_names = ["iccid"]

    iccid = models.CharField(max_length=22, unique=True, db_index=True)
    imsi = models.CharField(max_length=15, blank=True, db_index=True)
    msisdn = models.CharField(max_length=32, blank=True, db_index=True)
    carrier_profile = models.ForeignKey(
        to=CarrierProfile,
        on_delete=models.PROTECT,
        related_name="sim_cards",
    )
    router = models.ForeignKey(
        to=CellularRouter,
        on_delete=models.PROTECT,
        related_name="sim_cards",
        blank=True,
        null=True,
    )
    slot = models.CharField(max_length=16, choices=SIMSlotChoices, blank=True)
    provisioning_state = models.CharField(
        max_length=32,
        choices=ProvisioningStateChoices,
        default="planned",
        db_index=True,
    )
    activated_at = models.DateTimeField(blank=True, null=True)
    suspended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Model options."""

        ordering = ["iccid"]
        verbose_name = "SIM Card"
        verbose_name_plural = "SIM Cards"
        constraints = (
            models.UniqueConstraint(
                fields=("router", "slot"),
                condition=models.Q(router__isnull=False) & ~models.Q(slot=""),
                name="cellular_sot_unique_router_slot",
            ),
        )

    def __str__(self):
        """Return the masked ICCID."""
        return self.masked_iccid

    @property
    def masked_iccid(self):
        """Return a display-safe ICCID."""
        if len(self.iccid) <= 8:
            return self.iccid
        return f"{self.iccid[:4]}...{self.iccid[-4:]}"

    def clean(self):
        """Validate SIM identifiers and assignment state."""
        super().clean()
        digits = self.iccid.rstrip("F") if self.iccid else ""
        if not digits.isdigit() or not 18 <= len(digits) <= 22:
            raise ValidationError({"iccid": "ICCID must contain 18 to 22 digits."})
        if self.imsi and (not self.imsi.isdigit() or len(self.imsi) > 15):
            raise ValidationError({"imsi": "IMSI must contain at most 15 digits."})
        if self.slot and not self.router_id:
            raise ValidationError({"slot": "A slot can only be set when the SIM is assigned to a router."})


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class CellularOperationalSnapshot(PrimaryModel):
    """Latest normalized operational state for a cellular router.

    This model intentionally stores the latest snapshot only. Historical signal
    quality and byte counters belong in a telemetry backend such as Prometheus.
    """

    natural_key_field_names = ["router__device__name"]

    router = models.OneToOneField(
        to=CellularRouter,
        on_delete=models.CASCADE,
        related_name="operational_snapshot",
    )
    observed_at = models.DateTimeField(db_index=True)
    collector = models.CharField(max_length=128)
    registration_state = models.CharField(
        max_length=32,
        choices=RegistrationStateChoices,
        default="unknown",
        db_index=True,
    )
    rssi_dbm = models.SmallIntegerField(blank=True, null=True)
    rsrp_dbm = models.SmallIntegerField(blank=True, null=True)
    rsrq_db = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    sinr_db = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    observed_iccid = models.CharField(max_length=22, blank=True, db_index=True)
    payload_hash = models.CharField(max_length=64)

    class Meta:
        """Model options."""

        ordering = ["-observed_at"]
        verbose_name = "Cellular Operational Snapshot"
        verbose_name_plural = "Cellular Operational Snapshots"

    def __str__(self):
        """Return a compact display string."""
        return f"{self.router} observed at {self.observed_at:%Y-%m-%d %H:%M:%S}"
