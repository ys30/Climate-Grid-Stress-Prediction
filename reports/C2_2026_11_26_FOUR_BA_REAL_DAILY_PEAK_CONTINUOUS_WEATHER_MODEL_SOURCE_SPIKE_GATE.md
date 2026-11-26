# C-2 2026-11-26 | First actual daily continuous-load model, four BAs — scientific QA checkpoint

## Direct original-source execution

A new exploratory daily peak load model was **actually run** on the SHA-pinned 2020–2025 original EIA-930 × candidate ERA5 source: ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`, gz member SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. All 210,432 original four-BA hours were read. Analytic unit is a **complete 24-hour UTC day** (do not impute incomplete days). Complete days: AZPS 2,188/2,192; BPAT 2,192/2,192; CISO 2,174/2,192; SRP 2,178/2,192.

Within each BA and winter/nonwinter, observed daily **peak MW minus that BA-year-month's mean daily peak** is regressed on two separately month-demeaned linear hinge terms for the positive (warm) and negative (cold) daily-mean temperature anomalies, with the reference temperature being the same BA-year-month observed mean of *candidate-area ERA5*. Point slopes are descriptive MW per degree of positive/negative anomaly magnitude; sandwich SE clustered by ISO week, approximate only.

**Important: The primary full-original-source daily model is DISTORTED by rare original EIA930 spikes and MUST NOT be admitted as final statistical inference.**

### Raw source QA breakthrough

| BA | Source original observed UTC hour | Original MW | Source supplied anomaly flag |
|---|---|---:|---|
| AZPS | 2020-01-22 15:00 UTC | **101,412** | TRUE |
| AZPS | 2020-09-03 16:00 UTC | **21,020** | TRUE |
| SRP | 2023-06-03 20:00 UTC | **70,313** | TRUE |
| SRP | 2023-02-26 23:00 UTC | **68,520** | TRUE |
| SRP | 2023-02-27 00:00 UTC | **45,097** | FALSE |

The 2023-02-27 SRP neighbor hour is **not flagged** despite its proximity to a flagged high source hour. BPAT's previously documented **2020-11-25 23:00 UTC 11,742 MW** hour is also unflagged. Therefore existing source flags are only candidate indicators, not exhaustive approved correction lists.

Source flagged candidate **days** among otherwise complete days: AZPS 7, BPAT 0, CISO 1, SRP 23. Main model always retains original source; the two exclusion analyses are **sensitivity only**, not data deletion or operator confirmation.

### Actual sensitivity results (MW per 1°C negative daily-mean temperature anomaly; NOT causal)

| BA / season | Full original input cold slope | Remove source-flagged UTC days | Remove flagged and ±1 UTC-day neighbors |
|---|---:|---:|---:|
| AZPS winter | +21.02 | **+69.00** | +68.92 |
| BPAT winter | **+184.99** | +184.99 | +184.99 |
| CISO winter | +194.67 | +194.67 | +194.67 |
| SRP winter | +35.47 | **+52.65** | +49.93 |
| AZPS nonwinter | −147.80 | −142.99 | −143.12 |
| BPAT nonwinter | +50.27 | +50.27 | +50.27 |
| CISO nonwinter | −550.45 | −549.99 | −549.75 |
| SRP nonwinter | −175.67 | −162.37 | −161.86 |

Sensitivity RMSE: AZPS winter 3,232.90 → **438.07** MW after flagged-day exclusion; SRP winter 3,380.10 → **260.21** MW. In SRP nonwinter 3,356.07 → **247.26** MW; strong reason to prohibit automatic model admission on the raw daily peaks. CISO nonwinter 2,151 MW even after source-flag exclusion: additional model/missingness inspection required, and weather geography is still a candidate proxy.

### Model and scientific admission gates

- This is a **continuous-load descriptive model** responding to a question raised by zero cold×high-load cells in earlier binarized AZPS and SRP seasonal analyses; hinges avoid binary zero-cell separation.
- The source data remains original *bulk vintage*. The later EIA API disagreements are not resolved. No source-flagged or neighboring hours were rewritten or silently dropped from main results.
- Weekly cluster-robust approximations, with 6 calendar years, cannot be treated as validated causal confidence intervals. Neither the BA weather geography nor within-BA weather/load weighting has been approved.
- These are **not** temperature-related causal demand increments, quantified climate-change trends, blind out-of-sample predictions or final multi-BA model coefficients.
- Historical FERC714 respondent 21 hourly source independent confirmation and CMIP6 SSP/PyPSA scientific predictions remain pending.
- **C-1 remains frozen.**

## Files and execution

Actually executed in local scientific runtime:
- `c2_four_ba_daily_piecewise_source.py`
- `c2_four_ba_daily_flag_sensitivity.py`
- Full original day-model CSV, 24-row sensitivity result CSV, 4-BA daily coverage, extreme-hour review, and both execution logs.

Verified ZIP, CRC passes:
`C2_Four_BA_Real_Daily_Peak_Weather_Anomaly_Sensitivity_20261126.zip`, SHA-256 `e9d88caf98d71f8329103a8d60ff664702179d64353f88a13492e58a7e41a3d8`. The ZIP includes source-locked scripts and outputs, **not the 2.3MB original archive**; reuse the previously verified original archival ZIP for reproduction.

## Next highest priority

(1) Cross-vintage audit the AZPS/SRP spikes and unflagged neighbors against later API/EIA-930 or independent operator source. (2) Use robust event/day-level comparison with outlier-admission rules fixed before model fitting, account for full weather-area uncertainty. (3) Re-validate operating BA geography and PUDL FERC714 21 source hours before any causal climate/power-grid inference.
