# Security Audit Registry

This directory records release security audit findings for Lipford Nautobot Metrics.

## Current Audit

The current release audit is [`RELEASE-AUDIT-2026-06-05.md`](RELEASE-AUDIT-2026-06-05.md). The machine-readable registry is [`registry.yml`](registry.yml).

| Finding | Priority | Status | Summary |
| --- | --- | --- | --- |
| `LNM-SEC-2026-001` | `P2` | `upstream_constrained` | `PyJWT==2.12.1` remains through Nautobot's authentication dependency chain. |

## Audit Procedure

Run the following before each release:

```powershell
.\.venv\Scripts\poetry.exe check
.\.venv\Scripts\poetry.exe build
.\.venv\Scripts\poetry.exe run pip-audit --local
```

Update `registry.yml` and the release audit document when findings change.
