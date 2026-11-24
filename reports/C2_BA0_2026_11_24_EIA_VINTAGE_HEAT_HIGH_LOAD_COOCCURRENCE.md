# C-2 BA-0 — actual EIA-vintage impact on heat × high-demand overlap (2026-11-24)

**Executed on original, SHA-verified data, not synthetic fixture.** Read `C2_C2_EIA930_Dual_Vintage_210432h_Quarantine_2026_11_23.zip`, checked the inner source SHA256 `5a7fc7bf030cdac33131c480ca0c145db0b942db050e09bf1c5d1396994dbee1`, and analyzed only the **12 source-comparable EIA-930 BA×year cohorts**. The temperature series is real ERA5 2 m reanalysis under an *unapproved HIFLD 2018 candidate BA geography* — **not** certified historical load exposure.

## Reproducible descriptive method

For each verified BA×year, restrict to identical UTC hours where bulk and API demand are both numeric; fix the high-load threshold at the nearest-rank **95th percentile of old bulk demand in those common hours**, then apply **that exact same threshold** to old and API. Intersect high-load labels with ≥30°C and ≥35°C hours from the unapproved ERA5 candidate. Track **classification flips, not only net category counts**; weather-hot hours where either demand vintage is missing are counted as incomparable, never imputed as zero. This is an exploratory fixed-threshold sensitivity, not trained forecasting or validation.

### Actual results

| BA×year | Temperature | Old high-load hot hours | New API high-load hot hours | Net | Individual classification flips |
|---|---:|---:|---:|---:|---:|
| AZPS 2025 | ≥30°C | 428 | 437 | +9 | 17 |
| AZPS 2025 | ≥35°C | 256 | 257 | +1 | 9 |

AZPS 2025 baseline high-load 95th percentile = **6,860 MW**. On **2025-07-31**, common-hour API minus bulk average reported demand = **−1,024.667 MW**, while the unapproved candidate ERA5 2m temperature averaged **31.2786°C**, with **13 hourly values ≥30°C and 7 ≥35°C**. The difference materially changes event-level demand classification even when net annual categories change little. This is **not** evidence of an actual power-grid emergency.

Other affected coverage: SRP 2021 has **11** ≥30°C candidate-hot hours where either demand vintage is missing, and SRP 2025 has **2** ≥35°C candidate-hot missing-pair hours; these must not be reported as zero stress. Across all 12 cohorts: **24** threshold summaries, **4,380** day summaries, and **26** threshold-specific classification flips (not necessarily 26 distinct UTC timestamps). The other half of the 24 BA×year groups lack independent API comparison and are **not** claimed concordant.

## Deliverable and gates

Executed `analyze.py`; five actual-source tests passed (source SHA, cohort count, AZPS numeric findings, missing ≠ zero, CSV content reproduction). The locally delivered `C2_EIA_Source_Vintage_Heat_Load_CoOccurrence_2026_11_24.zip` contains code, tests, 3 result CSVs, machine-readable output, report and SHA manifest (package SHA256 `044203cfe4ac3c14bfbbed4a2c1bb7957d33358a2dc63e62b6759861117787d5`). The ZIP was reopened and contents were SHA-validated. The original dual-vintage source ZIP is a separately previously delivered file and is **not** part of this small analysis-only ZIP. The script references the original source under `/mnt/data/`; adapt path locally if needed.

**Strict non-admission:** Old 2018 candidate footprint is not certified BA operational/load-weighted geography; 2025 has been explored descriptively (not pristine blind holdout); no official source-vintage correction has been established; no fitted demand forecast, climate attribution, SSP/CMIP6 projection or PyPSA stress analysis has been done. **C-1 remains frozen**.

**Next priority:** audit historical dated operational BA geography and construct a source-vintage sensitivity plan for extreme overlap that can be preregistered before predictive evaluation; retain both EIA vintages without hidden replacement.
