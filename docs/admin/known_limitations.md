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
- `pylint-nautobot 1.0.0` declares Python `<3.14`, so the Pylint/App Config/
  migration lint stage runs on Python 3.13. The application runtime and unit
  test matrix remains on Python 3.14.
- Production v1 supports the validated Nautobot database scale and collector
  set documented above. Expanded scale targets and additional collectors are
  deferred to the v2 specification due October 1, 2026.
