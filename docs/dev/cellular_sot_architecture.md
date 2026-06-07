# Cellular SoT Architecture

## Reconciliation Contract

Vendor collectors map Cisco, Cradlepoint, Sierra, or other payloads into `NormalizedCellularRouter`. DiffSync adapters compare normalized operational observations against Nautobot desired state.

The following conflicts require explicit review:

- An observed ICCID differs from every assigned SIM.
- A vendor payload contains duplicate serial numbers or IMEIs.
- An interface does not belong to the selected device.
- Two SIMs target the same router slot.
- A delayed collector snapshot is older than the stored snapshot.

## Scalability

- Use `select_related()` and `prefetch_related()` for UI and adapter loads.
- Process vendor accounts in bounded synchronization scopes.
- Use distributed locks per vendor account.
- Keep high-cardinality historical telemetry outside Nautobot.
- Use row locks when assigning SIM cards or updating latest snapshots.

## Sensitive Data

ICCID, IMSI, and MSISDN values must not be used as Prometheus labels or written unmasked to general-purpose logs.
