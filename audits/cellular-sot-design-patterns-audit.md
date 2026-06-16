# Design Patterns Audit — Nautobot Wireless Cellular SoT App (`nautobot_cellular_sot`)

**Audit date:** 2026-06-07
**Source audited:** recovered from `refs/pull/30/head` (`dced31e`) of
`Lipford-Dutch/nautobot-app-custom-metrics` — PR #30 was closed with *"moved to
standalone cellular SoT repository."* The package's `.py` source no longer exists
in any branch or in the live working tree (only `.pyc` bytecode remains there),
so this snapshot is the authoritative source. Line citations were verified to
match (e.g. `services.py:81` = `get_cellular_summary`, matching the prior SOLID audit).
**Method:** manual read of every in-scope module + AST/structure cross-check.

> **Provenance caveat:** because the app now lives in a separate repository, the
> standalone repo's `main` may have diverged from this snapshot. Where that would
> change a finding, it is flagged. To confirm: diff the standalone repo's
> `nautobot_cellular_sot/` against `dced31e`.

---

## Scorecard

| Pattern | Present | Implementation | Verdict |
|---------|:-------:|----------------|:-------:|
| Adapter (structural) | ✅ | `VendorAdapter`, `NautobotAdapter` (DiffSync) | Correct |
| Strategy via Protocol | ✅ | `CellularCollector` injected into `VendorAdapter` | Correct (DIP) |
| DTO / Value Object | ✅ | `NormalizedCellularRouter` (pydantic), `RouterModel` (DiffSync) | Correct |
| Service Layer | ✅ | `services.py` functions | Mostly correct (1 SRP smell) |
| Command (task queuing) | ⚠️ | `ReconcileCellularInventory` Job | **Incomplete — stub** |
| Facade | ⚠️ | `get_cellular_summary()` | Overloaded (3 consumers) |
| Template Method | ✅ | `NautobotUIViewSet`/`NautobotModelViewSet` subclasses | Correct (framework) |
| Observer | ✅ | webhooks via `@extras_features` | Correct (declarative) |
| Decorator | ✅ | `@transaction.atomic`, `@field_validator`, `@property` | Correct |
| Repository | ➖ | Django ORM Managers (idiomatic, no custom repo) | Appropriate |
| Factory / Registry | ❌ | none for collector selection | **Missing — recommended** |
| Builder | ➖ | manual Prometheus text assembly | Minor extract opportunity |
| Singleton | ➖ | only framework-managed (logger, DB) | Appropriate |
| Proxy / lazy-load | ✅ | lazy querysets + `select/prefetch_related` | Correct |

Legend: ✅ correct · ⚠️ present but flawed · ❌ missing & wanted · ➖ intentionally absent / N/A.

**Headline:** the *structural* SSoT design is sound — DiffSync adapters depend on a
small injected collector `Protocol` (textbook DIP + Strategy). The gaps are all in
**wiring**: the Command (Job) never drives the adapters, there is no Factory to
select a collector, and there is no orchestration Facade for the diff/sync flow.

---

## Findings

### PATTERN-001 — Command pattern is a stub: the Job never invokes the adapters
**Patterns:** Command, Strategy, OCP · **Importance: 8/10**
**Location:** `jobs.py:18-25` (`ReconcileCellularInventory.run`); adapters at
`ssot/adapters/vendor.py:19`, `ssot/adapters/nautobot.py:9`.

`run()` only logs and returns a string — it never instantiates `NautobotAdapter`
or `VendorAdapter`, never calls `.load()`, and never runs a DiffSync `diff`/`sync`:

```python
def run(self, dryrun=True):
    mode = "dry-run" if dryrun else "apply"
    self.logger.info("Cellular reconciliation requested in %s mode.", mode)
    self.logger.warning("No vendor collector is configured in the base app. ...")
    return f"Cellular reconciliation requested in {mode} mode; no vendor collector configured."
```

The Strategy (`CellularCollector`) and Adapters exist but are **dead code from the
Command's perspective** — the app's headline feature (reconciliation) does
nothing. This is the root cause of the SOLID audit's OCP score (6/10).

**Remediation** — add an orchestration Facade and have the Command delegate to it.
Keep the "no collector configured" guard. Drop-in (new `services.py` helper):

```python
# services.py
from diffsync.enums import DiffSyncFlags
from nautobot_cellular_sot.ssot.adapters.nautobot import NautobotAdapter
from nautobot_cellular_sot.ssot.adapters.vendor import CellularCollector, VendorAdapter

def reconcile_cellular(*, collector: CellularCollector, dryrun: bool = True) -> dict:
    """Diff vendor-observed state against Nautobot desired state (Facade)."""
    source = VendorAdapter(collector=collector)
    target = NautobotAdapter()
    source.load()
    target.load()
    diff = target.diff_from(source)
    if not dryrun:
        target.sync_from(source, flags=DiffSyncFlags.CONTINUE_ON_FAILURE)
    return {"created": diff.summary().get("create", 0),
            "updated": diff.summary().get("update", 0),
            "deleted": diff.summary().get("delete", 0)}
```

```python
# jobs.py — run() body
collector = get_configured_collector()   # see PATTERN-002
if collector is None:
    self.logger.warning("No vendor collector configured; nothing to reconcile.")
    return "No vendor collector configured."
result = reconcile_cellular(collector=collector, dryrun=dryrun)
self.logger.info("Reconciliation %s: %s", "previewed" if dryrun else "applied", result)
return result
```

*Unable to verify* whether the standalone repo already wired this — if so, mark resolved there.

---

### PATTERN-002 — Missing Factory/Registry for collector selection (OCP)
**Patterns:** Factory, Strategy, OCP · **Importance: 7/10**
**Location:** none exists; consumers would hard-code a collector class. `CellularCollector`
Protocol at `ssot/adapters/vendor.py:12`.

Adding a vendor (Cisco, Cradlepoint, Sierra — named in the Protocol docstring)
currently has no extension point: there is no registry mapping a configured name
to a collector implementation, so selection must be edited into core code. The
Strategy is injectable but **unselectable** at runtime.

**Remediation** — a tiny registry keyed off `PLUGINS_CONFIG`, closed for
modification, open for new collectors via entry-point/setting:

```python
# ssot/collectors.py  (new)
from importlib import import_module
from django.conf import settings
from nautobot_cellular_sot.ssot.adapters.vendor import CellularCollector

def get_configured_collector() -> CellularCollector | None:
    """Resolve the collector named in PLUGINS_CONFIG (OCP extension point)."""
    cfg = settings.PLUGINS_CONFIG.get("nautobot_cellular_sot", {})
    dotted = cfg.get("collector_class")
    if not dotted:
        return None
    module, _, attr = dotted.rpartition(".")
    return getattr(import_module(module), attr)()
```

New vendors register by setting `collector_class` — zero core edits.

---

### PATTERN-003 — `get_cellular_summary()` Facade mixes aggregation + DTO shaping for 3 consumers
**Patterns:** Facade, SRP, OCP, DRY · **Importance: 7/10**
**Location:** `services.py:81-118`; consumers: `views.py:27` (UI),
`api/views.py:35` (summary), `api/views.py:47-63` (Prometheus).

One function builds the per-router dict (`:92-103`), aggregates SIM counts
(`:105-109`), and returns the API/UI response shape (`:110-118`). Worse, the
**registration business rule is duplicated**: `services.py:91` uses
`registration_state in {"registered", "roaming"}` and `api/views.py:58` re-derives
the identical rule independently:

```python
# services.py:91
registered_count += int(bool(snapshot and snapshot.registration_state in {"registered", "roaming"}))
# api/views.py:58  (duplicate of the same rule)
registration_up = 1 if router["registration_state"] in {"registered", "roaming"} else 0
```

Two places to change one rule. As operational metrics grow this Facade becomes the
brittle hot-spot the SOLID audit (SOLID-001) predicted.

**Remediation** — extract the rule and the row builder; keep the public function:

```python
# services.py
REGISTERED_STATES = frozenset({"registered", "roaming"})

def is_registered(snapshot) -> bool:
    """Single source of truth for 'registered' (used by summary and exporters)."""
    return bool(snapshot and snapshot.registration_state in REGISTERED_STATES)

def _router_row(router) -> dict[str, Any]:
    snapshot = getattr(router, "operational_snapshot", None)
    return {
        "id": router.pk, "device": router.device.name, "imei": router.imei,
        "provisioning_state": router.provisioning_state,
        "sim_count": router.sim_cards.count(),
        "registration_state": snapshot.registration_state if snapshot else "unknown",
        "observed_at": snapshot.observed_at if snapshot else None,
        "assignment_conflict": has_sim_assignment_conflict(router),
    }
```

Then `api/views.py:58` becomes `registration_up = int(router["registration_state"] in services.REGISTERED_STATES)`. One rule, one place.

> Note: `services.py:98` calls `router.sim_cards.count()` **per router inside the
> loop** while `:83` already `prefetch_related("sim_cards")` — the `.count()` issues
> an extra query per router (N+1), defeating the prefetch. Use `len(router.sim_cards.all())`.
> (Efficiency, importance 5/10 — folds into the same extraction.)

---

### PATTERN-004 — Prometheus exposition is hand-built in the view (Builder/SRP)
**Patterns:** Builder, SRP · **Importance: 3/10**
**Location:** `api/views.py:47-63` (`CellularPrometheusView.get`).

The view aggregates *and* formats the exposition text, including label escaping
(`:57`). Mixing transport (HTTP view) with serialization (text format) makes the
escaping logic untestable without an HTTP round-trip.

**Remediation** — extract a pure builder; the view just returns it:

```python
# services.py (or a new exporters.py)
def render_prometheus(summary: dict[str, Any]) -> str:
    """Render bounded-cardinality cellular metrics as Prometheus text."""
    lines = ["# HELP cellular_router_info Cellular router inventory marker.",
             "# TYPE cellular_router_info gauge", ...]
    for r in summary["routers"]:
        device = str(r["device"]).replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'cellular_router_registration_up{{device="{device}"}} '
                     f'{int(r["registration_state"] in REGISTERED_STATES)}')
        ...
    return "\n".join(lines) + "\n"
```

Now the escaping/label logic is unit-testable (see the testing audit, TEST-005).

---

### PATTERN-005 — Serializers expose all fields incl. sensitive identifiers (DTO/ISP)
**Patterns:** DTO, Interface Segregation · **Importance: 4/10**
**Location:** `api/serializers.py:13,21,29,37` (`fields = "__all__"`).

`SIMCardSerializer` exposes raw `iccid`, `imsi`, `msisdn` over the REST API, even
though the model deliberately provides `masked_iccid` (`models.py:158-163`) for
display safety. The DTO leaks more than any single consumer needs (ISP).

**Remediation** — make the SIM DTO explicit and add a masked read field:

```python
class SIMCardSerializer(NautobotModelSerializer):
    masked_iccid = serializers.CharField(read_only=True)
    class Meta:
        model = SIMCard
        fields = ["id", "url", "masked_iccid", "imsi", "msisdn", "carrier_profile",
                  "router", "slot", "provisioning_state", "activated_at", "suspended_at"]
```

*Unable to verify* whether downstream consumers depend on raw `iccid`; confirm before narrowing.

---

## Patterns that are correct (no action)

- **Adapter + Strategy + DIP** — `VendorAdapter.__init__(*, collector: CellularCollector)`
  (`vendor.py:25`) depends on the abstraction, not a concrete vendor. `RouterModel`
  (`ssot/models.py`) is the shared normalized value object. This is the strongest
  part of the design; keep it.
- **DTO at the boundary** — `NormalizedCellularRouter` (`schemas.py`) validates IMEI
  (`^\d{15}$`), signal-strength ranges, and normalizes ICCID before the ORM. Correct
  anti-corruption boundary.
- **Decorators** — `@transaction.atomic` + `select_for_update()` in
  `assign_sim_to_router` (`services.py:17-33`) and `ingest_operational_snapshot`
  (`services.py:36-70`) correctly guard concurrent SIM/slot conflicts.
- **Observer / Template Method / Proxy** — webhooks, the Nautobot viewset base
  classes, and lazy querysets are all idiomatic framework usage.

## Could a simpler solution work?
Yes, in one place: there is **no need for a custom Repository pattern** — Django
Managers already are the repository, and the code correctly uses them directly.
Introducing repositories here would add indirection without benefit. The missing
patterns (Factory + orchestration Facade) are about *completing* the existing
design, not adding new abstraction layers.
