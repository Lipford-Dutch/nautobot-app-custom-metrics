# Known Limitations

- The app stores moderate-volume observations in the Nautobot database. It is
  not a replacement for a high-cardinality time-series database.
- Native collectors currently cover Nautobot JobResult and ObjectChange data.
  Golden Config, SSoT, and Device Lifecycle Management adapters are optional
  future integrations.
- Collection uses lookback-window aggregation. Scheduling frequency and
  lookback values must be selected together to avoid gaps or overlapping
  interpretation.
- Retention is operator-triggered through a Nautobot Job and is disabled by
  default.
- `PyJWT==2.12.1` advisories inherited through Nautobot's dependency chain
  remain upstream-constrained. Deployments must track Nautobot security
  releases and record formal risk acceptance until the constraint is resolved.
