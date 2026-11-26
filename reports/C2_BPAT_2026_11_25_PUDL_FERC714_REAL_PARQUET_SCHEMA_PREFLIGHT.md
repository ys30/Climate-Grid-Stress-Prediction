# C-2 BPAT — PUDL v2026.10 fixed Parquet schema preflight (2026-11-25)

## Source verification performed

Official PUDL stable release [data access documentation](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html) confirms versioned data at `s3://pudl.catalyst.coop/v2026.10.0/`. Official [data dictionary](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html) documents `core_ferc714__respondent_id` fields `respondent_id_ferc714`, `respondent_name_ferc714`, `respondent_id_ferc714_csv`, `respondent_id_ferc714_xbrl`, `eia_code`; `core_ferc714__hourly_planning_area_demand` fields include `respondent_id_ferc714`, `datetime_utc`, `report_date`, `demand_mwh`. The `out` version fills gaps and is not valid for an unfilled observed-data cross-source test.

The exact S3 HTTPS Parquet original was attempted from this runtime on 2026-11-25 but local DNS resolution failed. The web preview can't download Parquet bytes. Thus **no verified source Parquet original SHA or BPAT respondent ID** was acquired. Neither the BPA official XLSX original nor a known GitHub Actions artifact carrying the fixed PUDL originals could be verified. Previous GitHub connector status attempts only query PR-triggered runs: empty results cannot establish CI failure or success.

## Genuine software issue corrected

The committed source intake previously marked `download_complete=true` during `respondent_review_required` discovery mode after reading only respondent metadata. It did **not inspect the hourly Parquet schema or verify any rows**, although it downloaded the complete file. A malformed/wrong hours table could appear successfully acquired.

Now `audit()` unconditionally constructs `pyarrow.parquet.ParquetFile(hours)`, validates all four necessary core-hourly columns, and requires `metadata.num_rows >= 1` **before** producing the respondent discovery output. Also fails if no BPA-name respondent candidate is present. Audit returns `source_hourly_parquet_schema_checked=true` and observed source-row count, separate from `EIA930_full_hourly_comparison_completed=false`.

Two new tests create actual **synthetic Parquet** files through PyArrow; one asserts schema discovery success without scientific approval, one asserts missing `demand_mwh` fails closed. With earlier nine synthetic contract methods, this test module now has **11** defined tests. GitHub CI includes PyArrow 21.0.0 and selects the full test module. **No verified execution status for these new tests** was obtained in this turn.

## Scientific decision

The fixed-release FERC-vs-EIA route is materially better documented and more resistant to wrong-table ingestion. However, this turn does not establish original FERC-714 observation availability, respondent identity, hourly mapping or six-year accuracy. EIA-930 2020–25 BPAT observed demand baseline remains independently archived; 2021/2023 EIA-vintage mismatches remain unresolved. PUDL curated FERC core is not a hash-certified BPA operator XLSX original, even if the S3 files are later authenticated.

**All historical operational geography, load-weighted exposure and model training gates remain BLOCKED**. 2025 already descriptively explored; no untouched holdout assertion. Climate attribution/SSP/PyPSA stress result not claimed. C-1 remains frozen.
