# Cellular SoT

`nautobot_cellular_sot` adds authoritative desired-state management for cellular routers, SIM cards, carrier profiles, and normalized latest-state observations.

## Ownership Boundary

| Data | Authoritative system |
| --- | --- |
| Router assignment, desired SIM, APN, provisioning lifecycle | Nautobot |
| Latest registration and signal snapshot | External collector, normalized into Nautobot |
| Historical signal and traffic metrics | Prometheus-compatible telemetry platform |
| Raw vendor payloads | Logging or object-storage platform |

Nautobot is intentionally not a high-frequency polling database. The app stores only the latest normalized operational snapshot.

## Models

- `CarrierProfile`: reusable carrier and APN desired state.
- `CellularRouter`: one-to-one extension of a Nautobot `Device`.
- `SIMCard`: protected SIM assignment and lifecycle state.
- `CellularOperationalSnapshot`: latest-only normalized collector observation.

## Initial Configuration

```python
PLUGINS = [
    "lipford_nautobot_metrics",
    "nautobot_cellular_sot",
]
```

Run:

```shell
nautobot-server migrate
nautobot-server check
nautobot-server test nautobot_cellular_sot
```

## SSoT Safety

The base reconciliation Job defaults to dry-run and does not apply vendor data until a vendor-specific normalized collector is registered. Duplicate serial numbers and IMEIs fail the source adapter load before any database mutation.
