"""Model validation tests for Nautobot Cellular SoT."""

from django.core.exceptions import ValidationError
from nautobot.apps.testing import TestCase

from nautobot_cellular_sot.models import SIMCard


class SIMCardValidationTestCase(TestCase):
    """Validate sensitive identifiers before database writes."""

    def test_invalid_iccid_rejected(self):
        """Reject non-numeric ICCIDs."""
        sim = SIMCard(iccid="not-an-iccid")
        with self.assertRaises(ValidationError):
            sim.clean()
