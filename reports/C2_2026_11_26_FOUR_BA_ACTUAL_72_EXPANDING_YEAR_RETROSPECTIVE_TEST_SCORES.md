# C-2 four-BA 2023–2025 retrospective expanding-year load validation — actual source execution (2026-11-26)

## New scientific milestone

For the first time, this project fitted on earlier calendar years and computed **errors on genuinely omitted future-year load observations**. This differs critically from the prior 336 leave-one-year-out *parameter-refit* experiment, which measured within-retained-data fit rather than predictions on omitted years.

Input original ZIP `C2_2020_2025_72_Month_Original_Source_Archive.zip`, SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`, original EIA-930/ERA5 gzip SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. Actually opened all **210,432 BA×UTC source hours** and derived **8,732 complete 24-hour BA×UTC days**. Neither missing original load nor any source anomaly was imputed or silently deleted.

- Four BAs AZPS/BPAT/CISO/SRP.
- Three pre-existing pressure targets: daily peak, intra-day empirical P95, and daily mean observed EIA930 MW.
- Expanding chronological training/test splits:
  - train **2020–2022** and test **2023**;
  - train **2020–2023** and test **2024**;
  - train **2020–2024** and test **2025**.
- Two **fixed** Ridge(alpha=10) model specifications in each fold: calendar-month categorical terms, weekend and linear time trend; versus those terms plus cold and warm hinges based on the candidate-area ERA5 daily mean temperature anomaly relative to a **monthly temperature reference computed only on earlier training years**. Continuous-feature normalization also fits **training only**.
- Total **72 real held-year model test scores** with 36 baseline/weather matched fold-target comparisons. The source scores and paired comparisons are saved as separate derived CSVs with SHA:
  - `retrospective_expanding_year_actual_test_scores_72.csv` SHA-256 `b55b77e228cc297f3df0fa931bb39a407308a1fc6da3279cc24cb9812f9f0a2e`.
  - `paired_weather_vs_calendar_MAE_36.csv` SHA-256 `6e0c09921d681d03f345c0cee5382ab0abb1968b78edff07b2085d821241f1da`.
- **Nine actually executed tests passed (9/9)**. Including deliberately changing every 2025 test-target daily peak by +100,000 MW while keeping input weather and training years untouched: the weather-model predictions remain byte-identical, providing a direct no-test-target-leakage check. The retrospective model and output path checks are also real-source tests.

### Actual out-of-year MAE results

Across 36 test cohorts, candidate observed-weather model lowered MAE relative to calendar+trend in **33/36**; **three failures**: CISO daily mean in **2025**, SRP daily peak in **2023 and 2024**. Do NOT suppress negative results.

| BA | Target | Calendar MAE averaged over 2023/24/25 (MW) | Weather MAE (MW) | Weather wins out of 3 |
|---|---|---:|---:|---:|
| AZPS | peak | 612.7 | 500.8 | 3 |
| AZPS | P95 | 470.4 | 383.5 | 3 |
| AZPS | mean | 363.0 | 304.4 | 3 |
| BPAT | peak | 519.2 | 473.7 | 3 |
| BPAT | P95 | 502.6 | 457.3 | 3 |
| BPAT | mean | 370.8 | 329.6 | 3 |
| CISO | peak | 1985.8 | 1867.9 | 3 |
| CISO | P95 | 1957.2 | 1842.3 | 3 |
| CISO | mean | 1374.6 | 1300.4 | 2 |
| SRP | peak | **1304.8** | 1320.0 | **1** |
| SRP | P95 | 489.6 | 403.0 | 3 |
| SRP | mean | 327.4 | 282.3 | 3 |

These are simple arithmetic means of three fold-level MAEs; each fold's number of valid days may differ.

### What this does NOT establish

This is a **true chronological held-year score** but **not a blind validation**: the project had previously inspected all 2023–2025 data. It is a **conditional load prediction with the test year's REALIZED candidate ERA5 weather supplied as a feature**, not an operational day-ahead weather forecast, future climate projection or a climate-causal model. Original EIA930 spike concerns (especially AZPS/SRP), API vintage differences, missing FERC714 respondent 21 hourly independent source and unapproved historical BA weather exposure geography remain. A future externally sealed validation cohort and formal admission protocol are still required.

The tested local, complete source-locked script is included in downloadable archive `C2_Four_BA_20261126_Actual_Expanding_Year_Backtest_72_Scores.zip` with 72-row scores, 36-row pairs, nine tests and logs, full derived SHA manifest. Archive SHA-256 `0a0b4d8b53dc61797c2353dac8298b24582b1935835645fb6702bb18abd97079`, ZIP CRC passed. Input source ZIP is separately archived in the project and not duplicated inside the results bundle.

GitHub aggregate: `results/source_only/C2_FOUR_BA_2023_2025_RETROSPECTIVE_EXPANDING_YEAR_WEATHER_VS_CALENDAR_MAE_SUMMARY.csv`. The actual executed script resides in the downloadable reproduction ZIP; CI on the GitHub aggregate file is not claimed.

**C-1 frozen, all formal causal/weather-geography/future SSP/PyPSA gates still blocked.**
