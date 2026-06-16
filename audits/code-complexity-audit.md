# Code Complexity Audit — `lipford_nautobot_metrics`

**Date:** 2026-06-07
**Scope:** `lipford_nautobot_metrics/` application package (excludes `tests/` and the
auto-generated `migrations/`, which are reported separately where relevant).
**Tree analyzed:** `main` @ `cd733ed` (canonical, on GitHub). The running lab
instance is your live `full-metric-catalog-dev` tree and differs slightly (see
[Verification caveat](#verification-caveat)).
**Tools:** `radon` 6.0.1 (cyclomatic, raw LOC, maintainability index),
`complexipy` (cognitive complexity), and an AST pass for function/class/file
sizes and the intra-package import-coupling graph.

---

## TL;DR

This is a **low-complexity, well-factored** codebase. Nothing exceeds the usual
red-line thresholds:

- **Cyclomatic:** max **6** (`MetricValue.clean`, `_upsert_metric_value`). 0 functions > 10.
- **Cognitive:** max **7** (`_upsert_metric_definitions`, `MetricValue.clean`).
- **Maintainability index:** every file grades **A** (lowest 46.45, `services.py`).
- **Sizes:** 1 function > 50 lines, 0 files > 300 lines, 0 classes > 500 lines.
- **Coupling:** clean layering, no cycles, no tight coupling.

The findings below are **maintainability/quality nits, not complexity hotspots.**
The single most actionable item is the 71-line, highly repetitive
`_upsert_sample_values` (Finding 1, importance 4/10). Everything else is 1–3/10.

---

## Metric tables (raw evidence)

### Cyclomatic complexity (radon cc) — top blocks
| Score | Grade | Location | Identifier |
|------:|:-----:|----------|------------|
| 6 | B | `models.py:99` | `MetricValue.clean` |
| 6 | B | `services.py:248` | `_upsert_metric_value` |
| 5 | A | `services.py:80` | `seed_sample_metrics` |
| 5 | A | `models.py:58` | `MetricValue` (class) |
| 4 | A | `services.py:116` | `get_metric_summaries` |
| 4 | A | `services.py:151` | `_upsert_metric_definitions` |
| 4 | A | `jobs.py:10` | `SeedSampleMetricData` (class) |

*71 blocks analyzed, average complexity **A (1.65)**. No block > 10. No `switch`/`match`
statements exist in the codebase; max nested-conditional depth is 2.*

### Cognitive complexity (complexipy) — non-trivial functions
| Cognitive | Location | Identifier |
|----------:|----------|------------|
| 7 | `services.py:151` | `_upsert_metric_definitions` |
| 7 | `models.py:99` | `MetricValue.clean` |
| 5 | `services.py:80` | `seed_sample_metrics` |
| 5 | `services.py:248` | `_upsert_metric_value` |
| 3 | `services.py:292` | `_apply_changed_fields` |

### Size metrics (AST)

- **Functions > 50 lines:** `services.py:175 _upsert_sample_values` — **71 lines** (only one).
- Next: `services.py:248 _upsert_metric_value` (42), `services.py:80 seed_sample_metrics` (34), `services.py:116 get_metric_summaries` (33).
- **Files > 300 lines:** none. Largest: `services.py` **299** (242 SLOC).
- **Classes > 500 lines:** none. Largest: `models.py:58 MetricValue` (54 lines).
- Template `dashboard.html`: 97 lines (within norms).

### Maintainability index (radon mi) — lowest grades
| File | MI | Grade |
|------|---:|:-----:|
| `services.py` | 46.45 | A |
| `models.py` | 47.00 | A |
| `api/views.py` | 65.59 | A |
| `urls.py` | 71.58 | A |
| *(all others)* | 81.99–100.00 | A |

### Intra-package coupling (import graph)
`Ce` = efferent (modules it imports), `Ca` = afferent (modules importing it),
`I = Ce/(Ce+Ca)` instability (0 = stable, 1 = unstable).

| Module | Ce | Ca | I |
|--------|---:|---:|--:|
| `services` | 2 | 3 | 0.40 |
| `models` | 1 | 1 | 0.50 |
| `choices` | 0 | 2 | 0.00 |
| `views` | 3 | 0 | 1.00 |
| `api.views` | 3 | 0 | 1.00 |
| *(leaf modules: filters, forms, tables, serializers, urls)* | 1 | 0 | 1.00 |

Reading: `choices` is a stable leaf (I=0, depended on by `models` + `services`) — correct.
`services`/`models` are the appropriately-central domain core. View/API modules are
unstable leaves (I=1) — also correct (nothing should depend on them). **No cycles,
no module with both high Ce and high Ca (no tight coupling).**

---

## Findings

### Finding 1 — `_upsert_sample_values` is long and repetitive
**Importance: 4/10** · `services.py:175-245` (71 lines)

The only function over 50 lines. Its cyclomatic (2) and cognitive (1) scores are
*low* — it isn't logically complex, it's **four near-identical 14-line blocks**
calling `_upsert_metric_value(...)`, one per metric, differing only in data
(definition key, value formula, context dict, notes). This is a copy-paste /
mixed-data-and-logic smell: adding a 5th seeded metric means cloning a block.

**Remediation** — move the per-metric specifics into a data table and loop. Drop-in shape:

```python
# services.py — module level, near DEFAULT_METRIC_DEFINITIONS
def _sample_value_specs(day_index: int) -> tuple[dict, ...]:
    """Per-metric sample observation specs for a given day offset."""
    return (
        {
            "key": MetricKindChoices.TIME_SAVED_PER_AUTOMATED_TASK,
            "value": Decimal("1.2500") + Decimal("0.2500") * day_index,
            "context": {
                "task_name": "VLAN provisioning",
                "manual_hours": "2.0000",
                "automated_hours": str(Decimal("0.7500") - Decimal("0.2500") * min(day_index, 2)),
            },
            "notes": "Sample ROI observation generated for v1 first-batch validation.",
        },
        # ... the other three specs, verbatim from the current blocks ...
    )

def _upsert_sample_values(definitions, sample_days, result) -> None:
    base = timezone.localtime(timezone.now()).replace(hour=12, minute=0, second=0, microsecond=0)
    start = base - timedelta(days=sample_days - 1)
    source = get_app_settings()["sample_metric_source"]
    for day_index in range(sample_days):
        recorded_at = start + timedelta(days=day_index)
        for spec in _sample_value_specs(day_index):
            _upsert_metric_value(
                metric_definition=definitions[spec["key"]],
                recorded_at=recorded_at,
                value=spec["value"],
                context=spec["context"],
                notes=spec["notes"],
                source=source,
                result=result,
            )
```

Cuts the function to ~12 lines and makes adding a metric a one-entry change. Behavior-preserving; existing `test_jobs.py` covers it.

---

### Finding 2 — `MetricValue.clean` mixes two validations with the highest cognitive load
**Importance: 3/10** · `models.py:99-111` (cyclomatic 6, cognitive 7 — joint-highest in the app)

The nesting (`if unit == PERCENT:` → `if value < 0` … → `if kind in {...} and value > 100`)
is the densest spot in the code. Still small, but a guard-clause flattening reads easier and drops cognitive load:

```python
def clean(self):
    """Validate metric observations before saving."""
    super().clean()
    if not self.metric_definition_id or self.metric_definition.unit != MetricUnitChoices.PERCENT:
        return
    if self.value < 0:
        raise ValidationError({"value": "Percent metric values must not be negative."})
    bounded = {MetricKindChoices.AUTOMATION_ADOPTION_RATE, MetricKindChoices.MANUAL_ERROR_RATE_REDUCTION}
    if self.metric_definition.kind in bounded and self.value > 100:
        raise ValidationError({"value": "Bounded percent metric values must be between 0 and 100."})
```

Same logic, one less nesting level. `test_models.py` already exercises all three branches.

---

### Finding 3 — `services.py` mixes write (seeding) and read (rollup) responsibilities
**Importance: 3/10** · `services.py` (299 lines, 242 SLOC — largest file, MI 46.45)

The module holds both the **seed/upsert** pipeline (`seed_sample_metrics`,
`_upsert_*`, the `DEFAULT_METRIC_DEFINITIONS` data literal at `:19-68`) **and** the
**dashboard read** path (`get_metric_summaries` at `:116`). Two responsibilities,
two consumers (jobs vs. views/api). It's under the 300-line line and cohesive
*enough*, but it's the file most likely to keep growing as metrics are added.

**Remediation (optional, low urgency)** — split along the read/write seam when it next grows:

```text
services/
  __init__.py        # re-export public names to keep imports stable
  seeding.py         # DEFAULT_METRIC_DEFINITIONS, seed_sample_metrics, _upsert_*
  rollups.py         # get_metric_summaries, get_app_settings
```

Keep `from lipford_nautobot_metrics.services import seed_sample_metrics, get_metric_summaries`
working via `__init__` re-exports, so `jobs.py`, `views.py`, `api/views.py` are untouched. Defer until the file crosses ~300 lines.

---

### Finding 4 — `_upsert_metric_value` hand-rolls get-or-create change tracking
**Importance: 2/10** · `services.py:248-289` (42 lines, cyclomatic 6, cognitive 5)

The manual `try: MetricValue.objects.get(...) except DoesNotExist:` + field diffing
is intentional — it powers the `values_created` / `values_updated` counters the job
reports, which Django's `update_or_create` can't return directly. **No change
recommended**; documented here only so it isn't mistaken for an accidental
re-implementation. If the counts ever become non-essential, `update_or_create`
would halve the function.

---

## Coupling & cohesion summary

- **Afferent/efferent:** computed above. The hub is `services` (Ca=3) feeding
  `jobs`, `views`, `api.views`; `choices` is the stable shared leaf. This is
  textbook layered structure for a Nautobot app.

- **Instability:** values are appropriate to each module's role (stable core,
  unstable edges). No module is simultaneously central and volatile.

- **Tight coupling:** none found — no import cycles, no god-module.
- **Single responsibility:** strong overall; the one mild exception is Finding 3
  (`services.py` read+write).

- **Cross-package efferent coupling** (to `nautobot.*` / `django.*`) is high but
  expected and unavoidable for a framework app — not a defect.

## What would change the verdict (honesty notes)

- **Unable to verify against the running instance:** the lab runs your live
  `full-metric-catalog-dev` tree, which seeds **2** metrics via `phase2_sample_job`,
  whereas `main`'s `services.py` defines **4** (`DEFAULT_METRIC_DEFINITIONS`,
  `:19-68`). If the live tree has materially refactored `services.py`, re-run this
  audit against that branch to confirm the size/cohesion findings still hold. The
  command to prove it: `radon cc services.py -s && radon raw services.py -s` on that branch.

- No GraphQL/job/management-command code beyond `jobs.py` was found, so those
  dimensions are N/A here (the models declare `graphql` via `@extras_features`,
  which Nautobot auto-generates — no app code to measure).

---

## Runtime verification (lab evidence)

Captured against the running lab (Nautobot **v3.1.3**, Django **5.2.15**) via a
headless Chromium attached to the lab's Docker network (`nautobot:8080`),
authenticated as `admin`. Script: [`development/screenshots.py`](../development/screenshots.py).

**Instance / app status**

- App enabled: `PLUGINS = ['lipford_nautobot_metrics']`; `PLUGINS_CONFIG` resolved
  (`sample_metric_days=3`, `sample_metric_source=…phase2_sample_job`).

- `nautobot-server check` → 0 issues; migration `0001_initial_metrics` applied; 24/24 unit tests pass.

**End-to-end data chain (seed → DB → service rollup → REST API), all consistent:**
| Metric | DB values | Service avg / latest | REST `summary` |
|--------|----------:|----------------------|----------------|
| `automation_adoption_rate` | 3 (45/50/55) | avg 50.0 / latest 55.0 | avg 50.0 / latest 55.0 |
| `time_saved_per_automated_task` | 3 (1.25/1.50/1.75) | avg 1.5 / latest 1.75 | avg 1.5 / latest 1.75 |

Total: **2 definitions, 6 values.** ORM, dashboard service, and `/api/plugins/lipford-nautobot-metrics/summary/` agree.

**Screenshots** (in [`audits/screenshots/`](screenshots/)):

- `01-dashboard.png` — Metrics Dashboard: Definitions=2, Values=6, summary table (latest/avg/target/samples/source).
- `02-metric-definitions.png` — Metric Definitions list view.
- `03-metric-values.png` — Metric Values list: all 6 rows across 2026-06-03/04/05, ascending seed pattern.
- `04-navigation-home.png` — home with the **Metrics** nav tab registered.
- `05-metric-definition-detail.png` — a definition detail page (NautobotUIViewSet ObjectFieldsPanels).

> Note: the dev instance runs with `DEBUG=True`, so the Django Debug Toolbar panel
> appears on the right edge of each screenshot — expected dev behavior, not a defect.

<a name="verification-caveat"></a>
## Verification caveat
File/line citations are from `main` @ `cd733ed`. Screenshots and runtime data in
the companion verification (below) come from the running lab (live dev tree), so
seeded-row counts differ from `main`'s 4-metric default by design.
