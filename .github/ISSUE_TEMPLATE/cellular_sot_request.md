---
name: Cellular SoT Request
about: Propose a cellular router, SIM, carrier, collector, or observability enhancement
labels:
  - "type: feature"
  - "area: cellular-sot"
---

### Environment

- Nautobot version: <!-- Example: 3.1.3 -->
- nautobot_cellular_sot version: <!-- Example: 0.1.0 -->
- Deployment type: <!-- Docker, Kubernetes, systemd, other -->
- Vendor or collector: <!-- Cisco, Cradlepoint, Sierra, carrier portal, custom collector -->

### Proposed Functionality

<!-- Describe the cellular SoT feature, collector, API endpoint, dashboard, or automation hook. -->

### Data Ownership

<!--
State which system owns each field:
- Nautobot desired state
- External collector observed state
- Manual review/conflict resolution
-->

### Normalized Payload Example

```json
{
  "external_id": "router-001",
  "serial_number": "ABC123",
  "imei": "123456789012345",
  "interface_name": "Cellular0/1/0",
  "iccid": "8901120200000000000F",
  "registration_state": "registered",
  "observed_at": "2026-06-07T12:00:00Z"
}
```

### UI and API Expectations

<!-- Note dashboard, Device detail panel, GraphQL, REST, Prometheus, webhook, export, or permission behavior. -->

### Operational Risk

<!-- Describe SIM reassignment risk, stale collector behavior, duplicate identifiers, sensitive data, or blast radius. -->
