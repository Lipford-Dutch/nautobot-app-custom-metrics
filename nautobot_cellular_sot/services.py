"""Service-layer helpers for Nautobot Cellular SoT."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from nautobot_cellular_sot.models import CellularOperationalSnapshot, CellularRouter, SIMCard
from nautobot_cellular_sot.schemas import NormalizedCellularRouter


@transaction.atomic
def assign_sim_to_router(*, sim: SIMCard, router: CellularRouter, slot: str) -> SIMCard:
    """Assign a SIM to a router slot with row-level conflict protection."""
    locked_sim = SIMCard.objects.select_for_update().get(pk=sim.pk)
    locked_router = CellularRouter.objects.select_for_update().get(pk=router.pk)

    conflicting_sim = (
        SIMCard.objects.select_for_update().filter(router=locked_router, slot=slot).exclude(pk=locked_sim.pk)
    )
    if conflicting_sim.exists():
        raise ValueError(f"{locked_router} already has a SIM assigned to {slot}.")

    locked_sim.router = locked_router
    locked_sim.slot = slot
    locked_sim.full_clean()
    locked_sim.save()
    return locked_sim


@transaction.atomic
def ingest_operational_snapshot(
    *,
    router: CellularRouter,
    payload: NormalizedCellularRouter,
    collector: str,
) -> CellularOperationalSnapshot:
    """Create or replace the latest operational snapshot for a router.

    Stale snapshots are ignored to prevent delayed collector batches from
    overwriting newer state.
    """
    locked_router = CellularRouter.objects.select_for_update().get(pk=router.pk)
    existing = CellularOperationalSnapshot.objects.filter(router=locked_router).first()
    if existing and payload.observed_at <= existing.observed_at:
        return existing

    payload_hash = _hash_payload(payload.model_dump(mode="json"))
    snapshot, _ = CellularOperationalSnapshot.objects.update_or_create(
        router=locked_router,
        defaults={
            "observed_at": payload.observed_at,
            "collector": collector,
            "registration_state": payload.registration_state or "unknown",
            "rssi_dbm": payload.rssi_dbm,
            "rsrp_dbm": payload.rsrp_dbm,
            "rsrq_db": payload.rsrq_db,
            "sinr_db": payload.sinr_db,
            "observed_iccid": payload.iccid or "",
            "payload_hash": payload_hash,
        },
    )
    locked_router.last_reconciled_at = timezone.now()
    locked_router.save(update_fields=["last_reconciled_at"])
    return snapshot


def has_sim_assignment_conflict(router: CellularRouter) -> bool:
    """Return true when latest observed ICCID disagrees with assigned SIMs."""
    snapshot = getattr(router, "operational_snapshot", None)
    if not snapshot or not snapshot.observed_iccid:
        return False
    return not router.sim_cards.filter(iccid=snapshot.observed_iccid).exists()


def get_cellular_summary() -> dict[str, Any]:
    """Return dashboard and API-ready cellular inventory health."""
    routers = CellularRouter.objects.select_related("device").prefetch_related("sim_cards", "operational_snapshot")
    router_rows = []
    conflict_count = 0
    registered_count = 0
    for router in routers:
        snapshot = getattr(router, "operational_snapshot", None)
        conflict = has_sim_assignment_conflict(router)
        conflict_count += int(conflict)
        registered_count += int(bool(snapshot and snapshot.registration_state in {"registered", "roaming"}))
        router_rows.append(
            {
                "id": router.pk,
                "device": router.device.name,
                "imei": router.imei,
                "provisioning_state": router.provisioning_state,
                "sim_count": router.sim_cards.count(),
                "registration_state": snapshot.registration_state if snapshot else "unknown",
                "observed_at": snapshot.observed_at if snapshot else None,
                "assignment_conflict": conflict,
            }
        )

    sim_counts = SIMCard.objects.aggregate(
        total=Count("pk"),
        active=Count("pk", filter=Q(provisioning_state="active")),
        unassigned=Count("pk", filter=Q(router__isnull=True)),
    )
    return {
        "router_count": len(router_rows),
        "registered_count": registered_count,
        "conflict_count": conflict_count,
        "sim_count": sim_counts["total"],
        "active_sim_count": sim_counts["active"],
        "unassigned_sim_count": sim_counts["unassigned"],
        "routers": router_rows,
    }


def _hash_payload(payload: dict[str, Any]) -> str:
    """Return a stable SHA-256 hash for an operational payload."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
