# C-2 BPAT — immutable PUDL FERC714 offline artifact replay (2026-11-25)

## Verified source status

Official PUDL v2026.10.0 documentation offers fixed-version Parquet files for `core_ferc714__respondent_id` and `core_ferc714__hourly_planning_area_demand`: https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html . The `core` table is preferred to imputed `out` hourly demand for strict observed-source comparison.

Direct S3 original binary retrieval was attempted again; the assistant runtime has no working S3 DNS/network access. No authenticated fixed-version PUDL FERC714 Parquet bytes, verified BPA respondent ID, original BPA XLSX, or complete FERC-vs-EIA hourly comparisons were obtained this turn. Earlier GitHub PR-filtered run visibility is insufficient to establish any push CI success. Do not substitute AskTheGrid preview values for original operator or authenticated PUDL source observations.

## Actually committed implementation

New `scripts/c2_bpat_pudl_ferc714_verify_archive.py` provides an **offline, read-only second-pass review** from a previously saved source directory and `PUDL_FERC714_BPAT_SOURCE_AUDIT_MANIFEST.json`. It:

1. Requires exactly the pinned `v2026.10.0` release, both and only two named core FERC714 original Parquet entries and source files, without symlinks.
2. Recomputes each exact stored Parquet file SHA-256 and byte count, refusing missing, damaged, version-swapped or silently replaced source files.
3. Reuses reviewed candidate metadata and strict hourly schema without selecting BPA identity on name alone. Without `--reviewed-respondent-id`, output explicitly states `respondent_review_required` and does **not** assert that an hourly comparison occurred.
4. Writes an independent JSON audit to a new directory without overwriting source originals; both source training and EIA-vs-FERC inference remain blocked.

New `tests/test_c2_bpat_pudl_ferc714_verify_archive.py` contains six synthetic-Parquet source-integrity cases: verified replay, explicit reviewed-ID audit, source tampering, missing file, wrong release and incorrect respondent ID. Existing eleven tests for initial acquisition remain in the workflow; **17 total defined tests** across these two modules, execution status **not yet confirmed**.

Updated `.github/workflows/c2-bpat-pudl-ferc714-fixed-release.yml` runs both test files, downloads the actual fixed release in GitHub Actions when possible, and reruns saved originals through the independent second pass before uploading initial source and replay artifacts. Artifacts have 30-day retention, so a permanent, immutable long-term archive still requires an explicit separately verified publication or durable storage plan.

**Important provenance distinction:** A locally computed SHA of a first-time downloaded PUDL file proves identity of bytes after acquisition, not that a PUDL-curated table equals the original BPA operator workbook or guarantees source metadata authenticity. Even successful replay does not approve historical BA operational geography, observed within-BA spatial demand, 2025 blind holdout, or model training. No climate attribution, CMIP6 SSP or PyPSA model inference is claimed. **C-1 frozen.**
