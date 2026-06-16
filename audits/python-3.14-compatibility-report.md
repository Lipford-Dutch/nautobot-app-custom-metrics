# Python 3.14 Compatibility Report — `lipford_nautobot_metrics`

**Date:** 2026-06-07
**Target runtime:** Python 3.14 (owner-requested)
**App:** `lipford_nautobot_metrics` (this repo, `main`)
**Method:** clean-room proof on `python:3.14-slim` (no reuse of the 3.12 lab env),
against the lab's PostgreSQL 17 + Redis 6.

---

## 1. Compatibility conclusion

**Python 3.14 is viable today for this app on Nautobot 3.1.3 — with ZERO code or
dependency changes.** Just build/run on 3.14.

- **Modern Python 3.14 target?** ✅ Yes — works as-is.
- **Standalone Django app?** No — it is a **Nautobot 3.x app** (uses
  `nautobot.apps.NautobotAppConfig`, not the legacy 1.x `nautobot.extras.plugins.PluginConfig`).

- **Nautobot app?** ✅ Yes (Nautobot 3.1.x, Django 5.2.x).
- **Unavoidable incompatibility?** ❌ None found.

> Important: the owner-supplied checklist references **Nautobot 1.x plugin
> semantics** (`PluginConfig`, `config = MyPluginConfig`, `min_version`/`max_version`,
> `installed_apps`/`middleware`/`caching_config` attrs). Those **do not apply** —
> this is a 3.x app. The 3.x-equivalent contract was verified instead (see §9).

## 2. Root causes found
**None.** No bug, no incompatibility, no deprecated stdlib/typing usage surfaced.
The codebase already declares `python = ">=3.10,<3.15"` and uses no APIs removed
or changed in 3.14.

## 3. Files changed
**None.** This was a proof exercise; the app required no edits to run on 3.14.

## 4. Dependencies changed and why
**None.** On Python 3.14 the existing pins resolve to a complete, consistent set
— every native dependency ships a `cp314` wheel (no source builds):

| Native dep | Version (3.14) | Wheel |
|------------|----------------|:-----:|
| cryptography | 48.0.0 | cp314 ✅ |
| cffi | 2.0.0 | cp314 ✅ |
| psycopg2-binary | 2.9.12 | cp314 ✅ |
| pillow | 12.2.0 | cp314 ✅ |
| nh3 | 0.3.5 | cp314 ✅ |
| rpds-py | 2026.5.1 | cp314 ✅ |
| charset-normalizer | 3.4.7 | cp314 ✅ |

`Django-5.2.15`, `nautobot-3.1.3` resolved unchanged. `pip check` → no broken requirements.

## 5. Tests added or updated
**None required.** The existing 24-test suite is the regression guard and passes
unmodified on 3.14. (If 3.14 becomes a CI target, the only change is a workflow
matrix entry — see §8.)

## 6. Commands run — final pass/fail

| Command (Python 3.14.5) | Result |
|--------------------------|--------|
| `python --version` | Python 3.14.5 |
| `pip install "nautobot>=3.1.0,<4.0.0"` (dry-run resolution) | ✅ full resolve, cp314 wheels |
| `pip install nautobot==3.1.3` (real) | ✅ installed |
| `pip install --no-deps .` (the app) | ✅ installed (`0.1.0`) |
| `python -c "import nautobot; import django; ..."` | ✅ nautobot 3.1.3 / django 5.2.15 / py 3.14.5 |
| `python -c "import lipford_nautobot_metrics"` | ✅ app import OK |
| `pip check` | ✅ No broken requirements found |
| `nautobot-server check` (DB-backed) | ✅ System check identified no issues (0 silenced) |
| `nautobot-server test lipford_nautobot_metrics` | ✅ **Ran 24 tests … OK** |

Baseline parity (Python 3.12, earlier this session): `check`, `post_upgrade`,
`migrate`, `makemigrations --check` (no drift), REST API, job discovery, and the
same 24 tests — all green. 3.14 matches 3.12 exactly.

## 7. Remaining risks

- **Very low — a published 3.14 image exists.** `ghcr.io/nautobot/nautobot-dev:3.1.0-py3.14`
  is published (py3.10–3.14 all exist), so the dev `Dockerfile`
  (`FROM ghcr.io/nautobot/nautobot-dev:${NAUTOBOT_VER}-py${PYTHON_VER}`) builds on
  3.14 with no change. The clean-room proof additionally confirmed a from-scratch
  `python:3.14` + pip install also works.

- **Low — treat as works-but-newest.** 3.14 is the newest CPython; keep the 24-test
  suite as the on-every-push guard (see §8) so any future dependency regression on
  3.14 is caught early.

- **Out of scope:** the extracted `nautobot_cellular_sot` app was not tested on 3.14
  (separate repo; source not in this workspace).

## 8. Manual follow-up (optional, to operationalize)
None required to *use* 3.14. To make it first-class:

1. Add `3.14` to the CI matrix in `.github/workflows/ci.yml` (the `check-in-docker`
   / `unittest` `python-version` lists) so the suite runs on 3.14 every push.

2. Optionally build the dev image on 3.14: `PYTHON_VER=3.14 invoke build` (the
   `Dockerfile` `PYTHON_VER` arg already supports it).

The `Programming Language :: Python :: 3.14` classifier and `<3.15` pin in
`pyproject.toml` are already present — no packaging change needed.

## 9. Plugin contract verification (3.x-equivalent of the owner checklist)

The checklist's 1.x attributes were mapped to the modern `NautobotAppConfig` contract:

| Owner checklist (1.x) | 3.x reality in this app | Status |
|-----------------------|--------------------------|:------:|
| `PluginConfig` subclass | `LipfordNautobotMetricsConfig(NautobotAppConfig)` (`__init__.py:11`) | ✅ |
| `config = MyPluginConfig` | `config = LipfordNautobotMetricsConfig` (`__init__.py:32`) | ✅ |
| `name`, `verbose_name`, `version`, `author`, `description`, `base_url` | all set (`__init__.py:14-19`) | ✅ |
| `required_settings`, `default_settings` | `required_settings=[]`, `default_settings={...}` (`__init__.py:20-24`) | ✅ |
| `PLUGINS = [...]`, `PLUGINS_CONFIG` | set in `development/nautobot_config.py:131-136` | ✅ |
| `jobs` | `register_jobs(...)` in `jobs.py` (3.x mechanism) | ✅ |
| `menu_items` | `navigation.py` `menu_items` | ✅ |
| `template_extensions` | n/a for this app (none defined) | ➖ |
| `graphql_types`, `custom_validators`, `caching_config` | declared via `@extras_features(...)` on models (3.x mechanism) | ✅ |
| `min_version`/`max_version`/`middleware`/`installed_apps` | **1.x-only attrs — not part of the 3.x contract** | ➖ N/A |

No hardcoded secrets; DB/Redis/secret-key all read from environment in
`development/nautobot_config.py`.
