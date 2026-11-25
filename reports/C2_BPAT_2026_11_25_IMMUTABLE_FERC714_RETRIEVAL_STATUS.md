# C-2 BPAT — FERC-714 original acquisition: immutable re-verification and honest workflow state (2026-11-25)

## What was actually checked

The BPA [official annual FERC-714 page](https://transmission.bpa.gov/business/operations/ferc714/default.aspx) continues to list 2020–2025 XLSX workbook links. The official site returns XLSX content type when following its direct links, but the available container cannot resolve `transmission.bpa.gov` to download original bytes; direct assistant file download failed as well. Thus **zero BPA original workbooks are newly authenticated** in this turn.

The GitHub connector checked the combined commit-status and associated PR-workflow runs for the BPAT intake workflow commit `fedfc670b6d49d23f7c569769bc0cf50af763e88` and later report commit `89ca535bb77670121167966888f63c46d327bb72`. Both returned empty status/run arrays. The connector is PR-filtered for associated runs; **empty arrays do not establish whether push/workflow-dispatch Actions executed**. There is no verified new Actions artifact ID to download. Do not describe the BPA downloader as green or a completed original-source acquisition.

## Actual code correction

Updated `scripts/c2_bpa_ferc714_original_acquisition.py` to ensure existing `BPA_FERC714_YEAR_ORIGINAL.xlsx` files are inspected *in place* rather than redownloaded/overwritten, recording `existing_original_reverified` when both XLSX structure and SHA pass. A damaged preexisting file is reported as `existing_original_invalid` and **not silently replaced** with possibly different current network bytes. Files not present still go through original URL download and workbook-source inventory. The manifest completeness gate and CLI exit-status gate accept the two valid categories only. Thus reruns preserve original operator source bytes, as required for source-vintage reproducibility.

Added two synthetic-only contract tests to `tests/test_c2_bpa_ferc714_original_acquisition.py` for immutable re-verification and corrupted original handling, raising the BPAT acquisition suite to **six test definitions**. GitHub Actions workflow still selects that test file and attempts six real official URL downloads; **no exact GitHub Actions run or six-test pass has been confirmed in this turn**.

## Why the stage cannot yet advance to actual FERC–EIA comparison

A 12-h cross-check from a *third-party* preview is not independently obtained BPA FERC-714 original XLSX. A small average 6.75 MW difference and the 25-offset clock sensitivity describe only those unverified displayed values. No 2020–25 FERC-714 original cells, SHA, sheet definitions, timezone/DST contract, respondent-area load definition, or six-year independent match are available for scientific claims.

**Next concrete gate:** obtain the source-original 2025 XLSX (then 2020–24), verify SHA and workbook cells; map raw respondent and hour-ending/local time onto EIA-930 UTC interval start; audit EIA vintage and completeness. BA operating geography/load-weighted exposure is a separate open gate. C-1 remains frozen, no modeling admission.
