# Testing Audit — Nautobot Wireless Cellular SoT App (`nautobot_cellular_sot`)

**Audit date:** 2026-06-07
**Source audited:** `refs/pull/30/head` (`dced31e`) — see the
[design-patterns audit](cellular-sot-design-patterns-audit.md) for provenance.
**Test files:** `tests/test_models.py`, `tests/test_schemas.py`, `tests/test_views.py`
(9 test methods total).

> **Exact line-coverage % — Unable to verify here.** The app is not installed in
> the running lab (only `.pyc` bytecode exists in the live tree; it is not in
> `PLUGINS`), so I did not execute the suite. To get the real number, run inside a
> lab with the app installed and enabled:
> ```bash
> nautobot-server test nautobot_cellular_sot --keepdb
> coverage run --source=nautobot_cellular_sot -m nautobot.core.cli test nautobot_cellular_sot
> coverage report -m
> ```
> The matrix below is a **structural** coverage map (callable → exercised?), which
> is verifiable from the source and is the actionable artifact regardless of the %.

---

## Executive summary

The 9 tests are **well-written but shallow**: clear names, clean Arrange-Act-Assert,
independent setup, no over-mocking. The problem is **breadth** — the app's core
business logic in `services.py` and the entire SSoT adapter layer are essentially
untested. Every existing data-path test runs against an **empty database**, so
aggregation, conflict detection, snapshot staleness, and reconciliation — the
features that justify the app — have **zero behavioral coverage**.

**Test-pyramid shape:** 2 fast unit tests (`SimpleTestCase`, schemas) · 7
DB-backed integration tests (`TestCase`) · 0 E2E. The base of the pyramid is too
narrow for the amount of untested service logic.

---

## Structural coverage map

| Callable | Location | Tested? | Gap |
|----------|----------|:-------:|-----|
| `NormalizedCellularRouter.normalize_iccid` | `schemas.py:24` | ✅ | — |
| IMEI pattern validation | `schemas.py:13` | ✅ (invalid only) | valid+signal-range bounds untested |
| `SIMCard.clean` (iccid branch) | `models.py:165` | ✅ (1 of 3 branches) | imsi & slot-without-router branches untested |
| `CellularSummaryView.get` | `api/views.py:26` | 🟡 empty only | auth-without-perm 403, populated rollup |
| `CellularPrometheusView.get` | `api/views.py:43` | 🟡 empty+token | populated output, label escaping, perm 403 |
| `CellularDashboardView` | `views.py:14` | ✅ auth matrix | populated render untested |
| `get_cellular_summary` | `services.py:81` | 🟡 empty only | conflict/registered/sim aggregation |
| `assign_sim_to_router` | `services.py:17` | ❌ | slot-conflict `ValueError`, locking, happy path |
| `ingest_operational_snapshot` | `services.py:36` | ❌ | stale-snapshot rejection, update-or-create, hash |
| `has_sim_assignment_conflict` | `services.py:73` | ❌ | conflict true/false paths |
| `CellularRouter.clean` | `models.py:98` | ❌ | imei/interface-device/inventory-item rules |
| `SIMCard.masked_iccid` | `models.py:158` | ❌ | short vs long masking |
| `VendorAdapter.load` | `ssot/adapters/vendor.py:30` | ❌ | duplicate serial/imei `ValueError`; no fake collector |
| `NautobotAdapter.load` | `ssot/adapters/nautobot.py:15` | ❌ | load from ORM |
| `ReconcileCellularInventory.run` | `jobs.py:18` | ❌ | dry-run/apply messaging |
| `DeviceCellularExtension.right_page` | `template_content.py:11` | ❌ | router present/absent |

Legend: ✅ covered · 🟡 partial (empty-state or single branch) · ❌ uncovered.

**Roughly 3 of ~16 significant callables are meaningfully covered.** The highest-risk
uncovered code is concurrency-sensitive (`select_for_update` conflict logic) and the
reconciliation seam.

---

## Findings

### TEST-001 — Core service logic in `services.py` is untested
**Importance: 9/10** · `services.py:17,36,73,81`

`assign_sim_to_router`, `ingest_operational_snapshot`, and
`has_sim_assignment_conflict` have **no tests**, and `get_cellular_summary` is only
asserted on an empty DB (`test_views.py:62-63` → `router_count == 0`). The
conflict-detection and snapshot-staleness rules are the app's reason to exist.

**Remediation** — add behavioral tests (real records, real assertions). Drop-in:

```python
# tests/test_services.py  (new)
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from nautobot_cellular_sot import services
from nautobot_cellular_sot.models import CellularOperationalSnapshot
from nautobot_cellular_sot.tests.factories import make_router, make_sim  # see TEST-004

class AssignSimTestCase(TestCase):
    def test_rejects_second_sim_in_same_slot(self):
        router = make_router()
        make_sim(router=router, slot="sim1")
        intruder = make_sim()
        with self.assertRaisesMessage(ValueError, "already has a SIM assigned to sim1"):
            services.assign_sim_to_router(sim=intruder, router=router, slot="sim1")

class IngestSnapshotTestCase(TestCase):
    def test_stale_snapshot_is_ignored(self):
        router = make_router()
        fresh = _payload(router, observed_at=timezone.now())
        services.ingest_operational_snapshot(router=router, payload=fresh, collector="t")
        stale = _payload(router, observed_at=timezone.now() - timedelta(hours=1))
        services.ingest_operational_snapshot(router=router, payload=stale, collector="t")
        snap = CellularOperationalSnapshot.objects.get(router=router)
        self.assertEqual(snap.observed_at, fresh.observed_at)  # newer kept
```

---

### TEST-002 — SSoT adapter layer has no tests (incl. the collector seam)
**Importance: 8/10** · `ssot/adapters/vendor.py:30`, `ssot/adapters/nautobot.py:15`

Neither adapter is tested, and the `CellularCollector` Protocol — the whole point
of the dependency-inverted design — is **never exercised with a fake**. The
duplicate-identifier guard (`vendor.py:35-38`, raises `ValueError`) is untested.
This is also the natural place mocking is *appropriate* (a stub collector), and it
is currently absent.

**Remediation** — a fake collector + load tests (no real vendor needed):

```python
# tests/test_adapters.py  (new)
from datetime import datetime, timezone as tz
from django.test import SimpleTestCase
from nautobot_cellular_sot.schemas import NormalizedCellularRouter
from nautobot_cellular_sot.ssot.adapters.vendor import VendorAdapter

class FakeCollector:
    def __init__(self, payloads): self._p = payloads
    def collect(self): return self._p

def _p(serial, imei):
    return NormalizedCellularRouter(external_id=serial, serial_number=serial, imei=imei,
                                    interface_name="Cellular0/1/0", observed_at=datetime.now(tz.utc))

class VendorAdapterTestCase(SimpleTestCase):
    def test_load_rejects_duplicate_serial(self):
        adapter = VendorAdapter(collector=FakeCollector([_p("S1","123456789012345"),
                                                         _p("S1","123456789012346")]))
        with self.assertRaisesMessage(ValueError, "Duplicate vendor serial number: S1"):
            adapter.load()

    def test_load_adds_unique_routers(self):
        adapter = VendorAdapter(collector=FakeCollector([_p("S1","123456789012345"),
                                                         _p("S2","123456789012346")]))
        adapter.load()
        self.assertEqual(len(adapter.get_all("router")), 2)
```

`NautobotAdapter.load` deserves a sibling DB test once factories exist (TEST-004).

---

### TEST-003 — Model `clean()` validation is largely uncovered
**Importance: 6/10** · `models.py:98` (CellularRouter), `models.py:165` (SIMCard)

`CellularRouter.clean` (IMEI digits, modem-interface-belongs-to-device,
inventory-item-belongs-to-device) is **untested**. `SIMCard.clean` only has its
ICCID branch covered (`test_models.py:12`); the IMSI-length and
slot-without-router branches are untested, as is `masked_iccid`.

**Remediation** — branch-complete the existing `test_models.py`:

```python
def test_slot_without_router_rejected(self):
    sim = SIMCard(iccid="8901120200000000000F", slot="sim1")  # no router
    with self.assertRaises(ValidationError):
        sim.clean()

def test_masked_iccid_masks_long_values(self):
    self.assertEqual(SIMCard(iccid="8901120200000000000F").masked_iccid, "8901...000F")
    self.assertEqual(SIMCard(iccid="8901").masked_iccid, "8901")  # short: unmasked
```

---

### TEST-004 — No test data factories → forces empty-state-only tests
**Importance: 6/10** · all DB tests

Building a `CellularRouter` requires a `Device` + `Interface` (+ optional
`InventoryItem`) and a `SIMCard` requires a `CarrierProfile`. With no factory
helpers, every author defaulted to empty-DB assertions
(`test_views.py:62-63, 22-30`). The missing fixtures are the structural reason
TEST-001/002/003 weren't written.

**Remediation** — one small factory module unblocks all populated-state tests:

```python
# tests/factories.py  (new)
from nautobot.dcim.models import Device, Interface  # plus Location/Role/DeviceType/Status setup
from nautobot_cellular_sot.models import CarrierProfile, CellularRouter, SIMCard

def make_router(**kw) -> CellularRouter:
    device = kw.pop("device", None) or _make_device()
    iface = Interface.objects.create(device=device, name="Cellular0/1/0", type="other")
    return CellularRouter.objects.create(device=device, modem_interface=iface,
                                         imei=kw.pop("imei", "123456789012345"), **kw)

def make_sim(router=None, slot="", **kw) -> SIMCard:
    profile = kw.pop("carrier_profile", None) or CarrierProfile.objects.create(
        name="P1", carrier_name="ACME", apn="internet")
    return SIMCard.objects.create(iccid=kw.pop("iccid", "8901120200000000000F"),
                                  carrier_profile=profile, router=router, slot=slot, **kw)
```

*Unable to verify* the exact required `Device` scaffolding (Location/Role/Status) from
the audited snapshot — mirror the metrics app's working `Device` setup, or Nautobot's
`create_test_device` helper, when wiring this up.

---

### TEST-005 — Missing error/edge/security tests
**Importance: 5/10** · multiple

Concretely absent, by category:

- **Error:** SIM slot conflict `ValueError` (`services.py:27`); duplicate serial/imei (`vendor.py:36,38`); stale snapshot path (`services.py:50`).
- **Permission edges:** `CellularSummaryView`/`CellularPrometheusView` authed-without-perm → 403 (`api/views.py:28-34, 45-46`). The dashboard has this test (`test_views.py:32`); the APIs do not.
- **Security — Prometheus label injection:** `api/views.py:57` escapes `\` and `"` in device names; no test feeds a device name containing quotes/backslashes to prove the escaping holds.
- **Security — serializer exposure:** assert the SIM API does/doesn't expose raw `iccid`/`imsi`/`msisdn` (ties to design PATTERN-005).
- **Performance:** lock down the N+1 noted in PATTERN-003 with `assertNumQueries`.

**Remediation** — examples:

```python
def test_prometheus_escapes_device_quotes(self):
    router = make_router(device=_make_device(name='odd"name\\x'))
    self.client.force_login(self.user)
    body = self.client.get(reverse("plugins-api:nautobot_cellular_sot-api:cellular-prometheus")).content.decode()
    self.assertIn(r'device="odd\"name\\x"', body)

def test_summary_query_count_is_bounded(self):
    for _ in range(5):
        make_sim(router=make_router())
    with self.assertNumQueries(3):           # fails today: .count() per router (PATTERN-003)
        services.get_cellular_summary()
```

---

## Test quality assessment (what's already good)

- **Naming & AAA:** every test name states the behavior (`test_stale_snapshot_is_ignored`
  style); bodies follow Arrange-Act-Assert cleanly. Keep this.

- **Independence:** per-`setUp` users, no shared mutable state, schemas use
  `SimpleTestCase` (no DB) — fast and correct tier choice.

- **Mock usage:** no inappropriate mocking of the ORM (good). The only mock that
  *should* exist — a fake `CellularCollector` — is the missing seam (TEST-002).

- **Mild anti-pattern:** `test_dashboard_renders_empty_state` asserts on template copy
  (`"No cellular routers are configured."`, `test_views.py:30`) — behavior-via-copy
  coupling; prefer asserting a stable element/`data-testid` if the empty-state text changes often.

## Improvement plan (priority order)

1. **TEST-004 factories** (unblocks everything) → then **TEST-001 services** → **TEST-002 adapters**.
2. **TEST-003** model `clean()` branch completion (cheap, no factories for SIMCard).
3. **TEST-005** error/permission/security/perf edges.
4. Wire `coverage` into CI with a floor (e.g. `--fail-under=80`) once the above land, so coverage can't regress.

> Target after plan: services + adapters at ~90% branch coverage; overall ~80%+.
> Current measured % is **Unable to verify** without running the suite (command above).
