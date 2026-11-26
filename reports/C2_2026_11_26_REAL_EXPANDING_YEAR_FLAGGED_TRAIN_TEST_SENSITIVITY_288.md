# C-2 | Real chronological four-BA train/test source-flag separation audit — 2026-11-26

## What was ACTUALLY executed

The local audit reran the already-established *real original-source* 2020–2025 four BA expanding-year regression, and separately evaluated two immutable-data **training QA scenarios** and two **test evaluation scenarios**. The locked source ZIP SHA-256 is `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`; the original hourly member gzip SHA-256 is `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

- BA: AZPS, BPAT, CISO, SRP.
- Three targets: observed EIA930 daily peak, empirical daily P95, daily mean MW.
- Actual held-calendar-year folds: train 2020–22→test 2023; 2020–23→2024; 2020–24→2025. Original test-year candidate ERA5 is supplied as observed input, not a weather forecast.
- Both fixed Ridge(alpha=10) models: calendar/month/weekend/trend and calendar+candidate ERA5 cold/warm hinges. Every climatology/scaler is fitted on **training years only**.
- Training QA variants: all original complete UTC days vs **sensitivity-only** exclusion of originally source-flagged training days.
- Test evaluation variants: full original test cohort vs **sensitivity-only scoring on unflagged test days**; test data exclusions do NOT change training models.
- Actual output: **288 score rows, 144 paired MAE contrasts, 48 3-fold aggregate rows**.

### Strong verification of previous findings

All **72 original calendar-year model scores** were recomputed and reconciled against the previous independently SHA-verified `retrospective_expanding_year_actual_test_scores_72.csv` (SHA-256 `b55b77e228cc297f3df0fa931bb39a407308a1fc6da3279cc24cb9812f9f0a2e`). Maximum absolute numerical discrepancy: **4.83 × 10⁻⁶ MW**. Six actually executed local integration/QA checks passed (6/6).

### The new SRP negative-result mechanism

Three-year average *daily peak* MAE, MW:

| Train-data QA | Test scoring | Calendar baseline | Calendar + observed ERA5 weather | Weather minus calendar |
|---|---|---:|---:|---:|
| All original | All test | 1304.84 | **1320.02** | +15.18 |
| All original | Only unflagged test dates | 957.55 | **973.27** | +15.72 |
| Exclude training flagged UTC dates (sensitivity) | All original test | 842.52 | **757.47** | −85.05 |
| Exclude training flagged UTC dates (sensitivity) | Only unflagged test dates | 480.53 | **395.00** | −85.53 |

The comparison shows that test-day screening alone **does not** reverse the weather model's loss for SRP. Removing flagged training days *in a deliberately labeled sensitivity fit* changes fitted coefficients sufficiently that weather improves relative to the calendar model. This is evidence of model vulnerability to source-flagged training data, **not proof these observations are erroneous or authorized for deletion**.

The observed-weather model improves over the calendar model on **33/36 original** paired fold×target cohorts and **35/36 flagged-train-excluded sensitivity** cohorts; preserve negative cases. For BPAT all four QA score specifications are identical because no source flags occur in its six-year original baseline. AZPS daily peak source-flagged-training sensitivity improves both models' average MAE; its relative weather-vs-calendar benefit shrinks. These distinctions make it inappropriate to claim a universal benefit from a specific QA scheme.

Flagged evaluation UTC days were explicitly counted: AZPS 2023 **4**; CISO 2025 **1**; SRP 2023 **12** and SRP 2025 **1**; remaining BA/test-year combinations **0**. This is not independent validation of the physical accuracy of those original flags.

### Reproducibility

- Local actually-executed programs: `c2_four_ba_expanding_year_backtest.py` and `c2_backtest_flagged_train_test_audit.py` plus six passing tests `test_flagged_train_test_audit.py`.
- Original full 2020–25 source ZIP is **not duplicated** in the output package; it is already archived separately.
- Self-contained derived-analysis package `C2_20261126_Real_ExpandingYear_TrainVsTest_Flagged_QA_288.zip`, SHA-256 `18d168bfac14f635bf027fbcf96c8b16d6d490346ec5bc4c6c581f689d3cdd32`, ZIP CRC verified.
- Package contains full 288-row score file, 144-row paired contrast file, 48-row aggregate, reproducible local code, previous 72-row reference, source/result SHA manifest and tests/logs.
- Github aggregates: `results/source_only/C2_FOUR_BA_2023_2025_EXPANDING_YEAR_TRAIN_FLAGGED_SENSITIVITY_24.csv`. This is rounded to three decimals; exact result bytes are in ZIP. The local executed script was not claimed byte-identical to any new Github script.

## Scientific admission

The same unresolved prerequisites persist: current EIA930 source flags are *candidates*, with some unflagged SRP/AZPS spike-family hours; neither operator original source nor reliable real FERC714 respondent21 hourly validation has been established, and candidate ERA5 BA geography is unapproved. The 2023–25 fold years were previously explored and not blind. The retrospective weather input is the real weather from the target year, not an operational forecast. No causal climate attribution, deployment validation, or future SSP/CMIP6-PyPSA prediction result should be inferred from these sensitivity statistics.

**C-1 frozen and untouched.**
