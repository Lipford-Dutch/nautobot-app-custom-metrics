"""Choice sets for Nautobot Cellular SoT."""

from nautobot.apps.choices import ChoiceSet


class ProvisioningStateChoices(ChoiceSet):
    """Provisioning lifecycle states for cellular resources."""

    CHOICES = (
        ("planned", "Planned"),
        ("ordered", "Ordered"),
        ("provisioning", "Provisioning"),
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("retired", "Retired"),
    )


class SIMSlotChoices(ChoiceSet):
    """Supported SIM slots."""

    CHOICES = (
        ("sim1", "SIM 1"),
        ("sim2", "SIM 2"),
        ("esim", "eSIM"),
    )


class CarrierAuthenticationChoices(ChoiceSet):
    """Carrier APN authentication types."""

    CHOICES = (
        ("none", "None"),
        ("pap", "PAP"),
        ("chap", "CHAP"),
    )


class RegistrationStateChoices(ChoiceSet):
    """Normalized cellular network registration states."""

    CHOICES = (
        ("unknown", "Unknown"),
        ("registered", "Registered"),
        ("searching", "Searching"),
        ("denied", "Denied"),
        ("roaming", "Roaming"),
        ("offline", "Offline"),
    )
