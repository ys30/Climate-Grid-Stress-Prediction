# C-2 BPAT — Lightweight PUDL fixed-release FERC714 respondent-discovery path (2026-11-25)

## Empirical blocker and method pivot

As of this audit, the fixed-release `core_ferc714__respondent_id` and `core_ferc714__hourly_planning_area_demand` original Parquet bytes have **not been downloaded** into this assistant runtime: direct S3 URL attempts fail DNS. No confirmed GitHub Actions run artifact has yet provided an independently authenticated BPA respondent identifier. The authentic BPA annual XLSX reports remain unavailable, and the prior 12-hour third-party preview is insufficient to certify original BA load.

The earlier CI approach copied complete multi-decade FERC714 hourly Parquet before reviewing BPA candidate IDs. That increases download, artifact-storage, and reproducibility burdens unnecessarily for **identity discovery**.

Official PUDL v2026.10.0 [Data Access documentation](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html) explicitly supports DuckDB `httpfs` read-only remote Parquet queries, requiring **path-style S3** (`URL_STYLE 'path'`) because the public bucket name includes dots. Versioned paths permit queries against `s3://pudl.catalyst.coop/v2026.10.0/`; no nightly source is used.

## Implemented and committed new route

- `scripts/c2_bpat_pudl_ferc714_remote_coverage.py` performs fixed-version anonymous read-only DuckDB S3 queries. Its default phase selects only BPA/Bonneville respondent-name **candidates**, preserving source respondent ID, CSV/XBRL native IDs and EIA code. It refuses zero or duplicate identities and writes a SHA-pinned **derived candidate CSV**, exact query text and source version.
- It does **not automatically approve BPA identity**. An explicitly supplied candidate ID can run an *optional* hourly metadata-only aggregate count over 2020–25; such counts are a **source-only diagnostic**, not a full FERC–EIA comparison. The default CI does **not** invoke this stage.
- All outputs state `full_original_parquet_bytes_downloaded=false`, `original_parquet_sha256_verified=false`, `respondent_identity_approved=false`, `EIA930_comparison_completed=false`, `model_training_permitted=false`. A checksum of a derived CSV is *not* a SHA checksum of original upstream Parquet.
- `tests/test_c2_bpat_pudl_ferc714_remote_coverage.py` defines **5 mocked no-network test cases** for discovery gate, bad ID, optional yearly aggregate, duplicate candidate and no overwrite.
- `.github/workflows/c2-bpat-pudl-ferc714-remote-coverage.yml` automatically invokes the default lightweight discovery on push or manual dispatch; installs DuckDB and uploads only small candidate/provenance files with 30-day retention. Its success and candidate content have **not yet been verified** through an Actions run.

## Scientific disposition

This code change is a **retrieval strategy improvement**, not empirical validation of FERC data. The actual next decision is whether the GitHub-run candidate output uniquely maps a documented PUDL FERC714 respondent to the BPAT balancing authority. Only after verifying that identity should yearly/hourly FERC source availability be queried and compared with already authenticated 2020–25 EIA-930 BPAT hours; UTC/DST and series semantics must be audited.

Even a successful PUDL query is a **curated FERC-714 series**, not evidence that an original BPA XLSX file was SHA verified. Historical BA operational polygons and geographically weighted load remain blocked; EIA source-vintage mismatches and 2025 holdout restrictions remain. C-1 remains frozen.
