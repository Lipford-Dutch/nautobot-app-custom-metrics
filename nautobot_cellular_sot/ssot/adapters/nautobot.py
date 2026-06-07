"""Nautobot-side DiffSync adapter."""

from diffsync import Adapter

from nautobot_cellular_sot.models import CellularRouter
from nautobot_cellular_sot.ssot.models import RouterModel


class NautobotAdapter(Adapter):
    """Load authoritative desired-state cellular records from Nautobot."""

    top_level = ["router"]
    router = RouterModel

    def load(self):
        """Load routers and assigned SIM state using bounded query counts."""
        routers = CellularRouter.objects.select_related("device", "modem_interface").prefetch_related("sim_cards")
        for router in routers.iterator(chunk_size=500):
            assigned_sim = next(iter(router.sim_cards.all()), None)
            observed_iccid = getattr(getattr(router, "operational_snapshot", None), "observed_iccid", None)
            self.add(
                RouterModel(
                    serial_number=router.device.serial,
                    imei=router.imei,
                    interface_name=router.modem_interface.name,
                    desired_iccid=assigned_sim.iccid if assigned_sim else None,
                    observed_iccid=observed_iccid,
                    provisioning_state=router.provisioning_state,
                )
            )
