# C-2 BPAT: Fixed-release FERC-714 core source route (2026-11-25)

## Evidence-based alternative to blocked BPA XLSX downloads

BPA's six operator XLSX originals remain **unretrieved and unverified** in the assistant runtime. The GitHub connector could not confirm a successful push-triggered BPA workflow or identify a corresponding verified original workbook artifact. The earlier 12-hour third-party preview and 25-offset clock analysis cannot be used as operator-original FERC714 validation.

**New independent structured source**: PUDL **v2026.10.0**, released 2026-10-14, explicitly incorporated 2025 FERC-714 XBRL source data. PUDL documentation describes `core_ferc714__hourly_planning_area_demand` with `respondent_id_ferc714`, `datetime_utc`, `report_date`, `demand_mwh`, and native CSV/XBRL respondent ID fields, including caveats about timestamp normalization and the form's hour 1–24 conventions. It also exposes `core_ferc714__respondent_id` with names and EIA linkage. Source docs:
- https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html
- https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html
- https://docs.catalyst.coop/pudl/en/v2026.10.0/release_notes.html

**Fixed, versioned raw PUDL output keys (not mutable nightly):**
- `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.10.0/core_ferc714__respondent_id.parquet`
- `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.10.0/core_ferc714__hourly_planning_area_demand.parquet`

The source product is curated by PUDL; **these are not unaltered BPA operator XLSX originals**, and PUDL's datetime cleaning must be accounted for in a formal comparison.

## Committed workflow, explicit source gate

- `scripts/c2_bpat_pudl_ferc714_fixed_release.py` acquires each fixed-release published Parquet file **without overwriting existing bytes**, computes SHA256 and retains full unmodified Parquet, parses candidate BPA respondents by name but refuses to choose automatically. In review mode it reports candidates and marks `respondent_review_required`; after **explicitly source-reviewed respondent ID** input, it requires a unique matching metadata row and audits unique UTC-hour counts, null demand and 2020–2025 spans. Outputs always `model_training_permitted=false`, `bpa_original_XLSX_verified=false`, `EIA930_full_hourly_comparison_completed=false`.
- `tests/test_c2_bpat_pudl_ferc714_fixed_release.py`: five **synthetic-only test definitions** cover fixed path, respondent alias, disallowed tables, overwrite protection and no-review source gate.
- `.github/workflows/c2-bpat-pudl-ferc714-fixed-release.yml`: push/dispatch tests then attempts actual immutable Parquet download and uploads entire original files, metadata and SHA manifest with 30-day retention. An empty PR-filtered commit-run status from the connector is not evidence of execution success or failure.

## What was NOT accomplished and what next

No actual `v2026.10.0` FERC714 Parquet was downloaded or processed in this assistant runtime, and no repository Actions run/artifact has been independently confirmed for this newly committed pipeline. Consequently no genuine BPA FERC hourly values, respondent identity, paired 2020–2025 FERC/EIA metrics, timestamp conversion validity or scientific model-readiness were newly established.

**Next empirical gate**: inspect the Actions artifact and validate its sha-pinned original PUDL Parquet, review the BPA `respondent_id_ferc714` mapping against actual respondent name and EIA code, then run the unfilled `core` hourly data against already frozen 2020–2025 EIA-930 demand, with UTC hour-shift and DST diagnostics. Do not use `out_ferc714__hourly_planning_area_demand` (which contains PUDL imputations) as independently measured raw source. Even completed validation would be *PUDL-curated FERC-714 vs EIA-930*, not original BPA XLSX authentication.

Separate source-vintage, historical BA operating geography and load-geolocation restrictions remain. No SSP or PyPSA climate-stress inference. **C-1 frozen**.
