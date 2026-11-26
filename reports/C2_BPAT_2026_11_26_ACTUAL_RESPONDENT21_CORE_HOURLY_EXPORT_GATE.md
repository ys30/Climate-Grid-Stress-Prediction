# C-2 BPAT — actual respondent-21 unfilled FERC hourly export pipeline (2026-11-26)

## Concrete task completed

Previous C-2 PUDL source workflow queried only respondent 21 annual **coverage aggregates**. It could not supply the actual hourly source rows needed by the newly completed EIA930 cross-source comparator. This turn adds the missing extraction operation and a separate CI workflow.

- `scripts/c2_bpat_ferc714_21_real_core_hour_export.py`: directly queries the fixed `v2026.10.0` public `core_ferc714__hourly_planning_area_demand.parquet` (unfilled source core, NOT imputed `out_ferc714`). Filters only `respondent_id_ferc714=21`, `report_date` 2020-01-01 to before 2026-01-01, and exports four original fields to an explicitly named CSV; no interpolation.
- Streams DuckDB result in bounded `fetchmany(10000)` batches; validates respondent identity, UTC conversion, unique hour across **all reporting years**, chronological hour, nonnegative finite source values and null preservation; records per-report-year rows, missing demand, UTC-year boundary spillovers, source query, pinned release URL, transport, derived CSV SHA-256 and byte count.
- Two network mechanisms, S3 and HTTPS Range, use the **same pinned source version**. Failure diagnostic JSON is kept in each directory and no-empty-result gate is used.
- `.github/workflows/c2-bpat-ferc714-21-real-core-hour-export.yml`: install pinned DuckDB, run synthetic input contract tests, try actual PUDL S3 and fallback HTTPS. Final job cannot be green on mere code test pass or diagnostic JSON: it requires actual nonempty hourly CSV with SHA matching its source-provenance manifest, and uploads source rows if present.
- `tests/test_c2_bpat_ferc714_21_real_core_hour_export.py`: eight synthetic/zero-network behavior tests. A separately authored local version was **actually executed: 8/8 passed**. The exact GitHub version's CI pass is **not** claimed or observed.
- Local reproducibility package `C2_BPAT_FERC714_Respondent21_CoreHourly_Export_2026_11_26.zip` contains tested local exporter and test file, test log, README and source hashes. ZIP CRC checked and SHA-256: `6457680d3bea50caa2839b0256760e103bf6daa762308bf051d19cb7b9c17970`.

## Actual sources and limits

The real EIA930 original bulk BPAT 2020–25 52,608-hour CSV from last phase was independently re-read this turn; its actual SHA-256 remains `65e51c15227eb9aae84ce65b35038ea458fd8e2fdb6c9608211268e8291761bc`. Four source fields match the SHA-locked EIA comparator input. **This does not remove old EIA source-vintage conflict or establish equivalent demand scope**.

The assistant tried the *actual* public HTTPS Parquet URL via direct request again in this turn and received a DNS resolution failure. No actual respondent 21 PUDL hourly row, hourly count, FERC/EIA matched-hour metric, source-original Parquet SHA, BPA raw operator XLSX, or confirmed successful GitHub push Actions artifact is available. Source-output status remains **NOT ACQUIRED**, and the new source query is **not a scientific validation claim**.

PUDL docs: https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html and https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html . FERC hourly source instructions specify fixed standard time in native filings; do not infer that PUDL-normalized UTC timestamps have same hour-start vs hour-end semantics as EIA930 original bulk. The 0h primary and +/-1h sensitivity are preconfigured for future matched-row diagnostics; no best-lag mining.

## Next empirical result needed

Obtain the actual workflow artifact CSV and source-provenance JSON; check years, duplicate hours, nulls, UTC-year spillovers and source hashes; pass the actual CSV to `scripts/c2_bpat_ferc714_21_vs_original_eia930_hourly.py` alongside the authentic 52,608-hour EIA-930 CSV. Compare pair-counts before error metrics, and explicitly discuss source-hour convention and planning-area versus BA boundaries. The previous cross-era respondent 122/21/C002357/1738 match is from authentic two-file Git evidence. No climate attribution/SSP/PyPSA model training. **C-1 frozen.**
