# Release Security Audit: 2026-06-05

## Executive Summary

The `v0.1.0` release candidate was audited after refreshing the active Poetry environment to Nautobot `3.1.3`. The previous June 2, 2026 report referenced an older Nautobot 2.x dependency graph and is no longer representative of this repository.

The current audit confirms that the previously documented high-impact Django, Nautobot, GitPython, Pillow, cryptography, and urllib3 advisories are resolved in the active release graph. One upstream-constrained dependency advisory remains for `PyJWT==2.12.1`.

## Audit Commands

```powershell
.\.venv\Scripts\poetry.exe show django nautobot cryptography gitpython pillow pyjwt urllib3
.\.venv\Scripts\python.exe -m pip install pip-audit==2.10.0
.\.venv\Scripts\poetry.exe run pip-audit --local
```

## Key Dependency Versions

| Package | Version |
| --- | --- |
| Nautobot | `3.1.3` |
| Django | `5.2.15` |
| cryptography | `48.0.0` |
| GitPython | `3.1.50` |
| Pillow | `12.2.0` |
| PyJWT | `2.12.1` |
| urllib3 | `2.7.0` |

## Current Findings

`pip-audit==2.10.0` reported the following after local packaging tooling was updated:

| Package | Version | Advisory IDs | Fixed version | Status |
| --- | --- | --- | --- | --- |
| PyJWT | `2.12.1` | `PYSEC-2026-175`, `PYSEC-2026-177`, `PYSEC-2026-178`, `PYSEC-2026-179` | `2.13.0` | Upstream constrained by `social-auth-core==4.8.7`, which is pulled through Nautobot's authentication dependency chain. |

## Resolution Notes

- `poetry update pyjwt social-auth-core social-auth-app-django --dry-run` did not resolve a newer `PyJWT`; the resolver kept `social-auth-core==4.8.7` and `PyJWT==2.12.1`.
- Local `pip` was updated to `26.1.2`, clearing the tooling-only audit finding.
- Release consumers should continue tracking Nautobot `3.1.x` patch updates and the Nautobot/social-auth dependency chain for the `PyJWT` remediation path.

## Release Decision

The app package itself does not directly depend on `PyJWT`; it depends on Nautobot `>=3.1.0,<4.0.0`. The remaining advisory is documented as an upstream-constrained known issue for the `v0.1.0` release.
