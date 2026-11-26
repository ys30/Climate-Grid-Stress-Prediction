# C-2 BPAT — fail-closed S3/HTTPS respondent discovery and source diagnostics (2026-11-25)

## Objective and current verified evidence

BPAT FERC-714 source discovery remains **source-not-obtained**: the fixed-release PUDL v2026.10.0 Parquet binary is not available in the assistant container. The public PUDL [data access documentation](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html) provides S3 read-only DuckDB paths; [v2026.10.0 release notes](https://docs.catalyst.coop/pudl/en/v2026.10.0/release_notes.html) expressly state 2025 FERC-714 XBRL inclusion. Official [data dictionary](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html) defines respondent/EIA codes and `core_ferc714__hourly_planning_area_demand`. No PUDL FERC original parquet SHA, verified BPA respondent ID, genuine BPA XLSX source SHA, or paired 2020–25 FERC/EIA numerical result is newly reported.

The connected GitHub status endpoint for last workflow edit commit `c775c8f3fcc1924f77d757554946a7ae1d0842fc` returned `statuses: []`; the commit-associated workflow-run query returned `workflow_runs: []`, and is limited to **PR-triggered** runs. Neither proves that push-triggered Actions succeeded or failed.

## Actual bug addressed: false-success query workflow and uninformative diagnostics

The existing dual-transport DuckDB query may fail at several distinct stages (extension install, S3 secret initialization, remote respondent table read, identity matching). Previously its source-only JSON had no failure stage and no exception reason. Additionally, with `continue-on-error` for the primary S3 attempt, it was important not to report success simply because the workflow proceeded to artifact upload without a real respondent candidate.

Changes committed in this turn:

1. `scripts/c2_bpat_pudl_ferc714_remote_coverage.py`: structured stage names throughout connection, `httpfs`, S3 secret, remote Parquet query, CSV writing and reviewed-ID coverage. On failure it leaves an always-written JSON with `status=QUERY_FAILED`, `failure_stage`, `error_class`, and truncated `error_message`. Does not mask or swallow original exceptions.
2. `tests/test_c2_bpat_pudl_ferc714_remote_coverage.py`: two mocked no-network tests for DuckDB connection failure and HTTP 403 during the remote respondent query; they assert failure-stage provenance and no false candidate SHA. Combined module now has **9 defined tests**, but their actual GitHub execution has **not been verified**.
3. `.github/workflows/c2-bpat-pudl-ferc714-remote-coverage.yml`: always-run final source evidence check independently parses the derived candidate CSV and corresponding JSON for both S3 and HTTPS directories and requires at least one nonempty source-discovery output with `status=RESPONDENT_REVIEW_REQUIRED`. If neither transport returns evidence, the workflow exits nonzero. The always-upload artifact step still preserves partial diagnostic JSON where available.

## Scientific decision and priority

This is a **workflow correctness and diagnosability fix**, not actual progress in BPA original-source acquisition. A CSV derived from PUDL remote query can begin identity review but is **not** a SHA-verified complete original Parquet. Even if a verified BPA respondent candidate appears, selecting a FERC respondent to represent the EIA-930 BPAT BA requires independent review of respondent ID, EIA code and reported load-series scope; FERC-714 reports planning areas, not necessarily the identical BA demand territory.

Next useful scientific result requires retrieving an actual successful candidate CSV and checking the respondent identity, then querying annual core hour coverage and comparing observed UTC hour values with archived BPAT EIA-930 source-vintage-separated records. Do not claim that 2025 is an untouched holdout, and do not treat any progress here as evidence of annually certified BA geography or load-weighted weather exposure. All E2 training/SSP/PyPSA model gates remain closed. **C-1 frozen.**
