# C-2 BPAT — verified 52,608 original EIA hours integrated with respondent 21 FERC714 source-only comparison contract (2026-11-26)

## Actual execution

- **Real EIA930 baseline used in test execution:** `BPAT_2020_2025_EIA930_AUTHENTIC_HOURLY_START_UTC.csv`, 52,608 actual BPAT UTC-start hours from the previously authenticated original bulk-vintage archive. SHA-256 `65e51c15227eb9aae84ce65b35038ea458fd8e2fdb6c9608211268e8291761bc`. Re-read and asserted unique timestamps and true six-year counts 8,784/8,760/8,760/8,760/8,784/8,760.
- **No authentic FERC hourly data newly acquired**. DNS for PUDL S3, GitHub Raw and Zenodo fails in current execution environment; DuckDB is not installed. No Push Actions run artifact was fetched. The FERC input to all local integration tests is **clearly synthetic**, not a measurement.
- **Actual local run:** eight source/EIA-integration tests executed successfully, `Ran 8 tests ... OK`. Tests cover real EIA baseline uniqueness/coverage, artificial exact-match pilot (only to prove the join), duplicate FERC hours, non-BPA respondents, report-year vs UTC spillover, null demand, disallowed year and missing provenance. **No real 2020–25 FERC-vs-EIA numerical errors were estimated.**
- **Verified local reproducibility package:** `C2_BPAT_FERC714_21_EIA930_Join_Ready_Verified_2026_11_26.zip`, SHA-256 `93a6f471bbb8d3a69c47c155c303f1278b52353b36303c4ffadb04e028d9a694`; ZIP CRC check succeeded. Contains complete real BPAT EIA CSV, locally tested Python compare module, 8 tests, test log, README and source-file SHA checks.

## GitHub actual changes

- `scripts/c2_bpat_ferc714_21_vs_original_eia930_hourly.py`: pinned genuine EIA input SHA; enforce exact FERC respondent candidate ID `21` with non-imputed core fields `respondent_id_ferc714,report_date,datetime_utc,demand_mwh`; by-`report_date` FERC annual cohorts; count crossing-UTC-year hours; refuse duplicate `(report_year,utc_hour)` rows; missing FERC demand remains missing. Reports fixed 0h reference plus -1h/+1h sensitivity with matched-hour counts, MAE and bias. Does not select the lowest-error shift automatically, approve BA footprint, or permit training.
- `tests/test_c2_bpat_ferc714_21_vs_original_eia930_hourly.py`: eight no-network **synthetic-FERC** regression definitions.
- `.github/workflows/c2-bpat-ferc714-21-eia-join-contract.yml`: separate synthetic tests and source contract job so a successful CI result cannot be mistaken for a real FERC source download.
- Both new GitHub script and workflow contents were fetched back from the actual linked repository, confirming their existence. GitHub CI run status is **not yet confirmed**. The local tested version in the ZIP and the GitHub version have equivalent intended gates, but **are separately authored, not byte-identical**; do not claim a passing local test means this exact GitHub version passed CI.

## Exact next empirical steps

1. Obtain the actual v2026.10.0 PUDL core hourly Parquet from GitHub Actions or a working external network connection and select respondent `21`, the now historically cross-verified BPA FERC respondent (legacy CSV 122, XBRL C002357, EIA numeric 1738).
2. Export real core rows to a CSV using all four named fields, preserve the fixed-release URL and actual source bytes SHA, and examine FERC reporting-year/UTC spillover and 2020–25 hourly coverage.
3. Run the strict join; report pair counts **before** metrics. The 0h shift is a provisional reference, not a verified FERC hour-ending convention. Assess whether FERC planning area and EIA930 BPAT BA have equivalent demand accounting before attributing any difference.
4. Historic 2020–25 operational geometry / load geography, EIA later API vs original vintage differences, untouched 2025 holdout, CMIP6 and PyPSA model admission remain unresolved.

**C-1 is frozen. No modeled climate/grid prediction or confirmed FERC errors claimed.**
