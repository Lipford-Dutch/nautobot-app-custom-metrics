"""Tests for collector payload normalization."""

from datetime import datetime, timezone

from django.test import SimpleTestCase
from pydantic import ValidationError

from nautobot_cellular_sot.schemas import NormalizedCellularRouter


class NormalizedCellularRouterTestCase(SimpleTestCase):
    """Validate the normalized collector boundary."""

    def test_normalizes_iccid(self):
        """ICCID values are trimmed and upper-cased."""
        payload = NormalizedCellularRouter(
            external_id="router-1",
            serial_number="ABC123",
            imei="123456789012345",
            interface_name="Cellular0/1/0",
            iccid=" 8901120200000000000f ",
            observed_at=datetime.now(timezone.utc),
        )
        self.assertEqual(payload.iccid, "8901120200000000000F")

    def test_rejects_invalid_imei(self):
        """Malformed IMEIs are rejected before reaching the ORM."""
        with self.assertRaises(ValidationError):
            NormalizedCellularRouter(
                external_id="router-1",
                serial_number="ABC123",
                imei="invalid",
                interface_name="Cellular0/1/0",
                observed_at=datetime.now(timezone.utc),
            )
