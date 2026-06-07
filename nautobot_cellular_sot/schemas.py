"""Validated normalized payload schemas for cellular collectors."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NormalizedCellularRouter(BaseModel):
    """Normalized collector payload for cellular router inventory and latest state."""

    external_id: str = Field(min_length=1, max_length=255)
    serial_number: str = Field(min_length=1, max_length=255)
    imei: str = Field(pattern=r"^\d{15}$")
    interface_name: str = Field(min_length=1, max_length=255)
    iccid: str | None = None
    carrier_name: str | None = None
    registration_state: str | None = None
    rssi_dbm: int | None = Field(default=None, ge=-140, le=-30)
    rsrp_dbm: int | None = Field(default=None, ge=-160, le=-40)
    rsrq_db: float | None = Field(default=None, ge=-40, le=0)
    sinr_db: float | None = Field(default=None, ge=-30, le=50)
    observed_at: datetime

    @field_validator("iccid")
    @classmethod
    def normalize_iccid(cls, value: str | None) -> str | None:
        """Normalize ICCID values from carrier and vendor systems."""
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None
