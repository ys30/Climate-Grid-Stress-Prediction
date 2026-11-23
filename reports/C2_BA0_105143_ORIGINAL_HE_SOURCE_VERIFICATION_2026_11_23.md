# C-2 BA-0 — Original EIA-930 hour-ending provenance audit (2026-11-23)

## New empirical source check

The old six-year EIA-930 × ERA5 archived panel was constructed from official **EIA gridmonitor six-month BALANCE CSV** files; the more recent annual BA archives came from the **EIA v2 electricity/rto/region-data API**, `type=D`.

All source bytes were reopened and verified against embedded SHA256 source manifests. For 12 canonical annual API source ZIPs, **105,143 preserved UTC-start rows were verified individually** against their matching original raw API hour-ending `source_period_utc` and `reported_demand_mw` fields:

- `raw HE period = UTC-start + 1 hour`, at exactly one-hour resolution;
- raw numeric / empty demand faithfully matches each UTC-start derivative;
- **zero raw API HE→UTC conversion discrepancies** were found across these retained rows;
- **one CISO 2021 missing UTC key** (`2021-11-07T05:00:00Z`) is traced to **absent original raw API HE period** (`2021-11-07T06`), not a derived CSV conversion deletion.

All **325 old bulk-derived versus newer API-source hourly discrepancies** are now indexed by the actual raw API HE labels, retrieval timestamps, and old bulk source file SHA references:

| Difference classification | Hours |
|---|---:|
| Different numeric values | 174 |
| Old bulk blank; newer API numeric | 99 |
| Old bulk numeric; newer API blank | 51 |
| Newer original API timestamp absent | 1 |
| **Total** | **325** |

Key unresolved comparison cases: AZPS 2025 **169 numeric changes**; CISO 2024/2025 **48 older-blank/newer-numeric hours each**; BPAT 2021/2023 later API contains **24-hour present-timestamp-but-blank-demand intervals**.

## What this does *and does not* prove

**Proven:** the retained newer API hour-ending source was accurately converted and demand values were carried unchanged. Two distinct publicly distributed EIA source formats were compared. The old panel's six-month original EIA source file hashes are recorded in its manifest, and its aggregated six-year CSV gzip hash is independently verified.

**Not proven:** EIA officially revised any individual value, or that the later API values are globally preferred. The older original half-year file bytes are not inside the six-year consolidated ZIP, so this audit compared the older archived *derived* values against newly verified raw API values, plus the saved old half-year source identities. Independent byte-level re-fetch or time-frozen bulk source files are needed to distinguish version changes from bulk-extract semantics.

The CISO 2021 raw `2021-11-07T06` omission occurs near DST transition but **no DST-cause claim** is made. No imputation or silent overriding of either vintage is permitted.

## Reproducibility

User-delivered ZIP `C2_EIA930_Original_HE_325_Conflict_Source_Proof_2026_11_23.zip`, **3,513,291 bytes**, SHA256 `c4d08ded60395c8b0566a6472af8f0fc7ec2523200d2ddda52243f13c4ca8875`, independently reopened and archive-tested. It contains 13 original source archive ZIPs (12 newer API BA-years plus the original older six-year consolidated archive), `c2_he_origin_audit.py`, source identity JSON, `12_ANNUAL_API_HE_CHECKS.csv`, `VERIFIED_325_API_HE_ORIGIN_DIFFERENCES.csv`, and the explanation report. Original data bytes are in the user delivery rather than committed to the public repository.

Next gate: compare raw original six-month EIA CSV record fields and revision snapshots with the raw API HE records, then resolve protocol for source conflicts; independently validate BA geography and demand weighting. No historical predictive-model, anthropogenic attribution, CMIP6 or PyPSA stress claim; C-1 remains frozen.
