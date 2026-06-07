"""Template extensions for core Nautobot objects."""

from nautobot.apps.ui import TemplateExtension


class DeviceCellularExtension(TemplateExtension):
    """Add cellular desired and operational state to Device detail pages."""

    model = "dcim.device"

    def right_page(self):
        """Render the cellular panel when the device is a cellular router."""
        router = getattr(self.context["object"], "cellular_router", None)
        if router is None:
            return ""
        return self.render(
            "nautobot_cellular_sot/inc/device_cellular_panel.html",
            extra_context={"cellular_router": router},
        )


template_extensions = [DeviceCellularExtension]
