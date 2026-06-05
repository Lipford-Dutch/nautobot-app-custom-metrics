# Security Remediation Registry

This directory records the critical and high dependency vulnerabilities identified for this project, the grouped bug tickets that own remediation, and the identifiers that future fixes should carry through branches, commits, pull requests, and release documentation.

## Identifier convention

Use the ticket primary key everywhere a remediation is referenced:

- Branch: `security/<ticket-primary-key>-<short-description>`
- Commit subject: `<ticket-primary-key>: <summary>`
- Pull request title: `<ticket-primary-key>: <summary>`
- Release note fragment: `changes/<ticket-primary-key>.security.md`
- Fix record: update the matching registry entry when the implementation branch, commit, or pull request exists

## Current campaign

The June 2, 2026 audit is captured in [`VULNERABILITY-REPORT-2026-06-02.md`](VULNERABILITY-REPORT-2026-06-02.md). The machine-readable association registry is [`registry.yml`](registry.yml).

| Ticket primary key | Owner | Priority | Root cause group | Planned branch | Vulnerability report |
| --- | --- | --- | --- | --- | --- |
| `TNSCM-SEC-2026-001` | `codex` | `P0` | Stale runtime dependency resolution | `security/TNSCM-SEC-2026-001-runtime-dependency-refresh` | `TNSCM-VR-2026-06-02` |
| `TNSCM-SEC-2026-002` | `codex` | `P1` | Stale build-tool dependency resolution | `security/TNSCM-SEC-2026-002-build-tool-refresh` | `TNSCM-VR-2026-06-02` |

## Bug tickets

### TNSCM-SEC-2026-001: Refresh vulnerable runtime dependencies

- **Owner:** `codex`
- **Priority:** `P0`
- **Problem summary:** The June 2025 Poetry resolution still installs vulnerable runtime packages. It includes one critical Django SQL-injection advisory and 23 high advisories across Django, Nautobot, GitPython, urllib3, Pillow, cryptography, and PyJWT.
- **Root cause:** The broad direct constraint `nautobot = "^2.0.0"` permits a newer compatible Nautobot release, but `poetry.lock` still resolves Nautobot `2.3.16` and stale transitive versions. The related advisories should be repaired and validated together because they share the runtime dependency graph and lockfile refresh workflow.
- **Suggested repair:** Update the supported Nautobot target to a patched compatible release, refresh `poetry.lock`, and verify that the resulting runtime dependency graph reaches at least the patched package versions recorded in `registry.yml`. If a patched transitive version cannot resolve while Python 3.8 support remains enabled, explicitly decide whether to constrain the dependency or revise the supported-Python policy.
- **Acceptance criteria:** Re-run the pinned Poetry-lock audit with both PyPI and OSV advisory services; confirm that every advisory associated with `TNSCM-SEC-2026-001` is absent; run the project test suite on supported Python versions; add `changes/TNSCM-SEC-2026-001.security.md`; update the fix record in `registry.yml`.
- **Planned branch:** `security/TNSCM-SEC-2026-001-runtime-dependency-refresh`
- **Documentation:** This section, `registry.yml`, and `VULNERABILITY-REPORT-2026-06-02.md`.

### TNSCM-SEC-2026-002: Refresh vulnerable build tools

- **Owner:** `codex`
- **Priority:** `P1`
- **Problem summary:** The development lock graph includes vulnerable versions of setuptools and wheel. Their advisories concern arbitrary file write and arbitrary file permission modification during package download or unpack workflows.
- **Root cause:** The lockfile contains stale development-tool versions. These packages are not the shipped app runtime, so they are separated from the P0 runtime repair while retaining the same audit campaign reference.
- **Suggested repair:** Refresh the Poetry development lock graph and verify that setuptools resolves to at least `78.1.1` and wheel resolves to at least `0.46.2`. Validate package build and development setup workflows after the refresh.
- **Acceptance criteria:** Re-run the pinned Poetry-lock audit with both PyPI and OSV advisory services; confirm that every advisory associated with `TNSCM-SEC-2026-002` is absent; build the package; add `changes/TNSCM-SEC-2026-002.security.md`; update the fix record in `registry.yml`.
- **Planned branch:** `security/TNSCM-SEC-2026-002-build-tool-refresh`
- **Documentation:** This section, `registry.yml`, and `VULNERABILITY-REPORT-2026-06-02.md`.

## Audit scope notes

- The dependency audit covers all 171 Poetry lock entries, the conditional `django-tables2==2.7.0` lock alternative, and `docs/requirements.txt`.
- The report intentionally opens tickets only for GitHub-reviewed `CRITICAL` and `HIGH` advisories. The audit also found lower-severity advisories that should be handled during the same lock refresh when compatibility allows.
- Container image vulnerabilities are not enumerated because no local container scanner (`trivy` or `grype`) is installed. The development container is not shipped as the app runtime, but its base image should still be scanned separately.
- Code-level Ruff security lint could not complete because `tns_custom_metrics/tests/test_basic.py` contains a pre-existing parse error. Repair that unrelated syntax issue before treating a Ruff security-lint run as complete.
