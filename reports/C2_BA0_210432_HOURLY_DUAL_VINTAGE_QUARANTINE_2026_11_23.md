# C-2 BA-0 — immutable dual-vintage demand quarantine and raw HE boundary accounting (2026-11-23)

## What was executed

Read **original** GitHub Actions artifacts: the 2020–25 72-month EIA-930/ARCO ERA5 consolidated source ZIP and 12 individually SHA-verified EIA-930 annual API ZIPs. Kept the original archives unchanged. Built a deterministic, gzip-compressed **210,432-BA-hour dual-vintage audit panel**, with original bulk-derived demand, newer API demand in verified annual cohorts, the original unapproved 2018-HIFLD ERA5 candidate temperature, UTC key, source-difference status, and explicit `historical_geography_approved=False` / `model_training_permitted=False` on every record.

### New source-clock discovery

The 12 raw API HE CSVs together have **105,155** source rows. Each contains one extra, legitimate *preceding calendar-year* UTC interval-start hour: original EIA HE `YYYY-01-01T00` is `(YYYY-1)-12-31T23:00Z`. The saved **year-scoped converted API CSVs correctly retain 105,143** rows (12 boundary carryovers not part of the selected year). These 12 source-boundary rows are **not** among the 325 within-year version conflicts. For the remaining actual source hours, raw API demand and HE labels match the saved interval-start values. The CISO 2021 one-hour API absence is independently preserved rather than imputed.

### Source vintage findings

- **13 distinct EIA six-month bulk filenames** referenced by the 72 monthly original source manifests; each has **one consistent SHA-256** across all month references within that original run. This is *within-archive hash consistency*, not proof that API and bulk distribution have the same numerical vintage.
- **12** separately sourced annual BA-year API cohorts have been compared at identical UTC hours. They occupy **105,144 expected target-year slots**: 104,787 equal numeric values, 32 both missing, **174 different numeric values**, **99 old empty/new API numeric**, **51 old numeric/new API empty**, and **1 missing API key**, totaling **325 differences**.
- The remaining **105,288** original 2020–25 slots have no independently verified newer API cohort in this audit, so are explicitly marked `API_YEAR_NOT_FETCHED_FOR_COMPARISON` and **not falsely considered identical**.
- AZPS 2025 accounts for 169 numeric differences; CISO 2024/2025 each for 48 old-empty/new-value differences; BPAT 2021/2023 include 24-hour API present-key / blank-demand clusters.
- Raw HE conversion was verified for each downloaded API source; neither official revision causes nor canonical choice of the two demand vintages has been established. Do **not** merge or interpolate either version into the scientific panel.

## User reproducibility delivery

The supplied **`C2_C2_EIA930_Dual_Vintage_210432h_Quarantine_2026_11_23.zip`**, SHA256
`2e61b850272495e9e1644f23d06a3bb1c3aa93229229974a0ac7aa00432eec4c`,
contains 21 items: original 13 source archives (12 yearly API ZIP + one six-year ZIP), the full side-by-side gzip CSV, 325-row conflict CSV, 24 BA-year cohort table, 13-file batch SHA lineage, JSON source identity/QA manifest, README, reproducer and tests. The three local source tests passed. An independent clean extraction and rerun produced **byte-for-byte identical** 210,432-row gzip output (gzip mtime fixed to zero, deterministic row order).

The full source data and application code are included in the **downloadable package**, not published into this repository; this GitHub report is a status/provenance index.

## Scientific gates

No 2020–25 BA operational boundary or load-weighted meteorological exposure has been approved. Existing ERA5 temperature is a provisional 2018-vintage BA control-area proxy; it is not certified demand exposure. AZPS 2023 remains a strict canonical source QA failure. Source comparisons and 2025 exploratory analyses cannot be described as pristine blind holdout validation. No model fitting, climate forcing attribution, SSP future prediction or PyPSA adequacy inference is claimed. **C-1 remains frozen**.

The next root-cause task requires contemporaneous *original* EIA six-month bulk source files matching archived historical SHA digests, or EIA/PUDL release-vintage evidence. Current byte identities establish discrepancy but do not prove revisions or operator corrections.
