# C-2 BPAT — real 52,608-hour EIA-930 comparison-ready source export and FERC report-year correction (2026-11-26)

## Actually rerun on the original EIA-930 source archive

The assistant's filesystem contained an actual source-backed snapshot `C2_BPAT_2020_2025_Real_EIA_Demand_Baseline_Source_Pack_2026_11_25.zip`. This turn read its embedded `inputs/C2_2020_2025_72_Month_Original_Source_Archive.zip` and uncompressed the authentic `C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz`.

Selected rows strictly where `ba == BPAT` (not inferred from utility/county geography), retaining `timestamp_utc_start`, `EIA930_original_demand_mw`, missing-demand flag, and source anomaly-candidate flag. Independently checked:

| Source QA | Direct observed result |
|---|---:|
| Actual BPAT source hours | **52,608** |
| Distinct UTC starting timestamps | **52,608** |
| Numeric positive demand rows | **52,608** |
| Missing-demand flagged rows | **0** |
| Anomaly-candidate flagged rows | **0** |
| 2020 hours (leap year) | **8,784** |
| 2021 / 2022 / 2023 hours each | **8,760** |
| 2024 hours (leap year) | **8,784** |
| 2025 hours | **8,760** |

The extracted observed hourly baseline is packed in the local downloadable archive `C2_BPAT_2026_11_26_EIA930_Join_Ready_Original_52608h.zip`, with `BPAT_2020_2025_EIA930_AUTHENTIC_HOURLY_START_UTC.csv`, `PROVENANCE_AND_JOIN_GATE.json` and `README.md`. Provenance:
- Original outer ZIP SHA-256: `4c61e2a2b587c580f50e28483542608a88e8fe3d54ed13141073353ea7eef916`
- Exact nested source hourly GZIP SHA-256: `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`
- Output BPAT hourly CSV SHA-256: `65e51c15227eb9aae84ce65b35038ea458fd8e2fdb6c9608211268e8291761bc`

## Important actual software correction — report year != UTC calendar year

The published PUDL v2026.10.0 FERC-714 core-hourly schema has both `report_date` and `datetime_utc`, and PUDL explicitly describes cleaning T24 to next-day T00, meaning some source reporting-year hours can fall into adjacent UTC calendar year. Official docs: https://data.catalyst.coop/preview/pudl/core_ferc714__hourly_planning_area_demand and https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html .

Prior `scripts/c2_bpat_pudl_ferc714_remote_coverage.py` mistakenly used `year(datetime_utc)` to **filter and group** the data to '2020–25', making year-boundary hours leak to neighboring reporting years. This turn corrected to filter using `report_date >= DATE '2020-01-01' AND report_date < DATE '2026-01-01'` and group using `year(report_date) AS report_year`. Separately reports `utc_outside_report_year_rows` where the UTC timestamp year differs from report year. Updated mocked contract test to assert the exact SQL and boundary metric. GitHub source commit `80decb3` and tests commit `e47e15b`.

### Remaining genuine empirical gates

The observed 52,608-hour EIA-930 series uses **UTC start-of-hour** timestamps. Any eventual FERC-714 `datetime_utc` should be tested under candidate -1/0/+1 hour lag conventions **without picking the best alignment post hoc as a scientific result**, with pre-specified primary convention and sensitivity alternatives. FERC planning area and BPAT EIA balancing authority may still have different load scopes. EIA vintage discrepancies recorded previously remain separately quarantined; this export uses archived *original bulk-vintage* data only, not newer API replacement.

The true respondent identity chain is now archived and verified: **historical FERC CSV respondent 122, numeric EIA 1738 -> PUDL respondent 21 -> XBRL C002357**. An Actions query against v2026.10.0 respondent 21 core hourly remains submitted but **has not yielded independently checked actual FERC hourly rows**. Do not claim 2020–25 FERC coverage, matching errors, independent BPA original XLSX, operator-approved BA geometry, climate attribution or SSP/PyPSA training.

**C-1 remains frozen.**
