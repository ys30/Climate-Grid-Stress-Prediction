# C2 E0 January boundary repair and source anomaly gate — independently CI verified

Date: 2026-11-12. GitHub Actions success: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43314896382

## Why prior annual gaps were not random missing data
EIA-930 official six-month files partition records by reporting local/date boundaries. Reconstructing UTC start-hour January coverage from only same-year Jan–Jun and Jul–Dec balance files produced repeated apparent 7–8 missing hour keys per BA-year. Adding the **prior calendar year's Jul–Dec official file** resolves the 2023 and 2024 January timestamp gaps for all four BA. Source conflicts detected: **zero**.

**Corrected 2023 coverage:** AZPS 8758/8760 (2 genuine blank), BPAT 8760/8760 (0 blank), CISO 8758/8760 (2 blank), SRP 8760/8760 (0 blank). Each BA has **zero missing timestamp keys** after boundary reconciliation.

**Corrected 2024 coverage:** AZPS 8784/8784 (0 blank), BPAT 8784/8784 (0 blank), CISO 8736/8784 (48 blanks), SRP 8736/8784 (48 blanks). Each BA has **zero missing timestamp keys** after boundary reconciliation.

## Source candidate anomalies
A simple 2× neighboring-hour ratio flags **33 raw candidate outliers in 2023**, and **0 in 2024**, based on the full BA-year audit. These are data-issue *candidates*, not proven erroneous; do not automatically interpolate or silently delete.

Verified examples:
- SRP 2023-06-03 20:00 UTC: 70,313 MW; prior 4,597 MW; next 5,021 MW; ratio **14.62113×**. Must quarantine pending official validation.
- AZPS 2023-04-27 20:00 UTC: 9,854 MW; prior 3,031 MW; next 3,595 MW; ratio **2.97434×**.
- SRP 2023-07-22 00:00 UTC: 40,613 MW; neighbors 7,735 / 7,790 MW; ratio **5.23195×**.
- All such anomalies remain in original source snapshots, with a separately reported candidate flag and model-hold status.

## Remaining missing values
- 2023: AZPS 2 blank, CISO 2 blank.
- 2024: CISO 48 blank, SRP 48 blank.
- 2024 CISO first reported blank starts 2024-11-01 07:00 UTC; review its entire continuous missing window and co-occurrence with SRP before extreme-event model eligibility.

## Required follow-through
1. Upgrade the six-year official source coverage pipeline to include **previous year's H2** in *all* BA-years and compute revised annual admission. Current prior six-year coverage run is correct only for its limited source-list assumption, not UTC-complete after this newly discovered boundary effect.
2. Keep raw outlier candidates quarantined in the analysis-ready loader until a dated, reproducible source adjudication decision is made. Annual source coverage alone never authorizes model training on source errors.
3. Use train/validation/test on fixed calendar years only; inspect 2024–25 source issues strictly for QA, never choose models/hyperparameters based on test error.
4. No climate-change attribution or future SSP-derived grid stress claims have yet been estimated.

**Interpretation:** boundary reconciliation is a positive engineering result, not an imputation. Missing original demand cells and suspicious isolated peaks remain genuine source QC blockers.
