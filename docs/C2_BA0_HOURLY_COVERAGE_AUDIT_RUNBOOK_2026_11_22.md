# C-2 BA-0 — hourly UTC coverage audit: executable handoff (2026-11-22)

This instrument is an **inventory**, not evidence of a verified historical weather-demand panel. Do not make model or causal claims from a successful unit test.

## Input schema

Demand CSV (separately sourced from EIA-930):

```csv
ba,utc_start,demand_mw
CISO,2020-01-01T00:00:00Z,22000.0
```

Weather-proxy CSV (separately sourced and documented ERA5 extraction):

```csv
ba,utc_start,weather_value
CISO,2020-01-01T00:00:00Z,12.3
```

**Examples are illustrative and must never be treated as observations.** Input timestamps must represent UTC **interval starts** (the audit checks syntax and uniqueness but cannot prove the source's hour-ending semantics). A weather value must be labelled by variable/unit and geospatial proxy specification in its external manifest. No row should be fabricated or imputed to fill gaps.

## Execute

```bash
python -m unittest discover -s tests -p 'test_c2_ba_hourly_join_audit.py' -v
python scripts/c2_ba_hourly_join_audit.py \
    --demand data/private/eia930_ba_utc_demand.csv \
    --weather data/private/era5_ba_proxy_utc.csv \
    --out reports/generated/c2_ba_hourly_join_inventory.json \
    --bas CISO,AZPS,BPAT,SRP \
    --start-year 2020 --end-year 2025 --min-fraction 0.98
```

Threshold 0.98 is a **provisional inventory screen**, not an approved scientific acceptance threshold. Must explicitly preregister an appropriate BA-year coverage threshold *before* examining the target panel. The program does not grant approval on coverage alone. A bad UTC timestamp is logged and excluded; audit both input-error counts and duplicate counts before interpretation.

## Mandatory separate evidence

For each input provide a provenance manifest with publisher URL/API request, query parameters, access date, revision/vintage, row count, SHA256, field definitions, BA membership and timestamp conventions. For weather, report reanalysis version, variable units, ERA5 grid cells and fixed-site or polygon extraction weighting; proxy does not imply load-weighting. For EIA-930, explicitly document whether source time is hour-ending and how it was converted to interval-start UTC. Keep holdout 2024–2025 demand values unavailable to model selection.

## Required interpretation

- Per-BA-year `expected_hours` should be 8760 or 8784, based on UTC calendar year.
- `paired_valid_hours` counts only rows with both finite values, without imputing blank weather.
- Duplicate BA×UTC-hour keys invalidate the associated pairing, including if one duplicate is blank.
- `coverage_pass` tests only paired coverage and duplicates; it does **not** certify observation correctness, source provenance, temporal semantics or scientific feasibility.
- `model_training_permitted` is always `false` by design.
- 2020–2022 train / 2023 tune / 2024–2025 held-out is still **proposed**, subject to independent source coverage, revision consistency and pre-fit freeze.
- C-1 remains frozen. County/geographically load-weighted response and future scenario projection remain blocked by their independent gates.

No actual data CSVs, no observed coverage statistics and no skill scores were included in this change.
