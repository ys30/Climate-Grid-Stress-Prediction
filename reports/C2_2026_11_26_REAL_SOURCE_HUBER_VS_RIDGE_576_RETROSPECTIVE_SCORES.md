# C-2 real-data Ridge vs Huber cross-year source-immutable robustness — 2026-11-26

**Scope and result:** executed on the actual previously SHA-locked 210,432-hour original EIA930 + candidate-area ERA5 2020–2025 four-BA archive; 8,732 valid 24-hour BA-days. No original source row removed or changed in the all-original condition. New historical model comparison: 576 scored cohort-model-evaluation rows, 288 observed-weather versus calendar MAE pairs, 96 averaged fold outcomes and 48 pair-level summaries. Eight actual local QA integration tests passed, including consistency of all prior 288 Ridge scores (the 288 prior scoring rows in 4-BAs × 3 years × 3 targets × 2 training variants × 2 weather models × 2 test scoring subsets). Maximum numerical discrepancy **4.83 × 10^(-6) MW**. All Huber fits converged.

## Correct, narrow interpretation

Earlier source-QA results showed SRP weather+Ridge losing to calendar+Ridge on the original daily-peak target. This follow-up tests an *estimator*, not a new weather proxy, by retaining source spikes in Huber training data rather than requiring their deletion.

| BA | Train sample | Estimator | 2023–25 mean calendar test MAE MW | Mean weather-augmented test MAE MW |
|---|---|---|---:|---:|
| SRP | All original | Ridge | 1304.84 | **1320.02** |
| SRP | All original | **Huber** | 819.70 | **736.30** |
| SRP | Source-flagged training days omitted **sensitivity only** | Ridge | 842.52 | 757.47 |
| SRP | Source-flagged training days omitted **sensitivity only** | Huber | 825.29 | 740.46 |
| AZPS | All original | Ridge | 612.68 | 500.80 |
| AZPS | All original | Huber | 499.33 | 410.10 |
| BPAT | All original | Ridge | 519.17 | 473.74 |
| BPAT | All original | Huber | 520.98 | 465.33 |
| CISO | All original | Ridge | 1985.83 | 1867.91 |
| CISO | All original | Huber | 1961.66 | 1856.72 |

Huber fitted on normalized training targets and standardized training-only features; fixed `HuberRegressor(epsilon=1.35, alpha=10)`, compared to established `Ridge(alpha=10)`. Hyperparameters are **not independently tuned**, and numeric alpha values across distinct objectives cannot be treated as equal regularization strength. Only test years later than all training years are evaluated: 2020–22→2023, 2020–23→2024, 2020–24→2025. Training-only monthly candidate-temperature reference and scaler, with **realized test-year weather** supplied.

The original all-source weather estimator beats the corresponding calendar estimator on **33/36 Ridge** and **35/36 Huber** matched BA×year×target test groups; this is exploratory and evaluated on previously inspected years. SRP source spikes are still *unverified physical observations*. Good Huber prediction does not validate their authenticity, establish true 2023 test blindness, weather-area spatial weights, causal effect identification or future SSP/PyPSA simulation.

## Reproducibility

Local actually-executed program `c2_huber_ridge_source_robustness.py` imports the exact preceding `c2_four_ba_expanding_year_backtest.py` and checks the dual original-source SHA-256: ZIP `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`, gz `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. Self-contained RESULTS and code archive `C2_20261126_FourBA_Original_Huber_Ridge_576_Actual_Backtest.zip` **does not duplicate the original source input archive**. Bundle SHA-256 `7f83a2c55c80807ca8bbd4c62def7bf7b01e3a990acb3a664cc5c9bc8ea00fa0`, ZIP CRC good.

Contains exact 576 row scores, 288 matched weather/calendar pairs, 96 three-year average rows, 48 averaged pairs, original-source executable programs, tests (8/8), logs, readme and output hash manifest. GitHub independently stores the reduced source-only peak summary at `results/source_only/C2_2026_11_26_HUBER_VS_RIDGE_SOURCE_IMMUTABLE_DAILY_PEAK_RETROSPECTIVE.csv`. No GitHub CI success is claimed for the local programs.

**Scientific decision:** Continue to report original Ridge baseline. Add pre-specified Huber estimator robustness arm, do not post-select a winner based on these inspected results. Source anomaly validation and geographic BA exposure approval remain open hard gates. C-1 frozen; C-2 climate causality and SSP/PyPSA predictions blocked.
