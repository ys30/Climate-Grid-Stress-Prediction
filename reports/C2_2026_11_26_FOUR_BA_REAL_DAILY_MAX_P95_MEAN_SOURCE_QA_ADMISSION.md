# C-2 daily peak versus P95 versus mean — REAL-source QA target robustness, 2026-11-26

## Executed on actual 2020–2025 EIA930 × candidate ERA5 original hourly archive

Source ZIP SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`, hourly GZIP SHA `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. Reconstructed all BA × complete 24h UTC-day records from 210,432 source hours. Compare **exactly the same complete days** for each of three different outcome variables: daily maximum, within-day empirical P95, and daily mean MW. Daily candidate-area ERA5 mean temperature anomaly and cold/warm piecewise regressors are demeaned within each BA's year-month. For each BA × winter/nonwinter × target, run the original-complete-day baseline AND an additional **sensitivity-only** exclusion of days with source flags. 4 × 2 × 3 × 2 = **48 real observational model fits**.

### Winter slopes, MW per one degree candidate cold anomaly magnitude

| BA | Target | Original all complete days | Exclude source-flagged UTC dates | Original model RMSE MW | Flag-excluded model RMSE MW |
|---|---|---:|---:|---:|---:|
| AZPS | Daily peak | 21.02 | 69.00 | 3232.90 | 438.07 |
| AZPS | Intra-day P95 | 61.42 | 61.09 | 323.32 | 323.65 |
| AZPS | Daily mean | 43.21 | 45.11 | 197.28 | 146.90 |
| BPAT | Daily peak | 184.99 | 184.99 | 416.29 | 416.29 |
| BPAT | Intra-day P95 | 180.90 | 180.90 | 366.71 | 366.71 |
| BPAT | Daily mean | 152.03 | 152.03 | 276.01 | 276.01 |
| SRP | Daily peak | 35.47 | 52.65 | 3380.10 | 260.21 |
| SRP | Intra-day P95 | 68.18 | 48.38 | 696.62 | 241.06 |
| SRP | Daily mean | 39.73 | 38.77 | 210.74 | 143.81 |
| CISO | Daily peak | 194.67 | 194.67 | 1184.88 | 1184.88 |
| CISO | Intra-day P95 | 204.32 | 204.32 | 1160.65 | 1160.65 |
| CISO | Daily mean | 178.39 | 178.39 | 1098.77 | 1098.77 |

**New scientific QA implication:** For AZPS winter, changing from daily maximum to empirical intra-day P95 substantially reduces reliance on one extreme source hour: cold association changes 21.02→69.00 MW/°C for max, versus 61.42→61.09 for P95. **But P95 is not universally robust**: SRP's multi-hour high-load spikes still affect P95 (68.18→48.38). The daily mean is more stable for SRP but answers a *different grid-pressure question*, not instantaneous peak stress. Official C-2 pressure metrics should pre-specify daily max **plus** intra-day P95 and mean as complementary diagnostics rather than silently replace peak with P95.

Nonwinter all-source versus flagged-day results are in `results/source_only/C2_FOUR_BA_DAILY_TARGET_PEAK_P95_MEAN_SOURCE_QA_20261126.csv`. These are purely descriptive fitted source associations and model residual summaries, not climate-change causal effects.

## Actual test/packaging provenance

The executed local `c2_daily_target_robustness.py` reran the full actual original dataset, produced all 48 rows and a 24-row slope/RMSE leverage comparison. **Six local original-source-derived tests passed**, verifying both original byte hashes, complete factorial grid, AZPS peak-v-P95 leverage, SRP multi-hour-spike P95 limitation, BPAT source-flag semantics and exact same-day sample across outcomes.

Self-contained ZIP `C2_20261126_FourBA_Daily_Peak_P95_Mean_Real_Source_Sensitivity.zip` includes the **original archived source ZIP**, exact locally executed script, both result CSVs, six actual test definitions and results, run log and SHA manifest. File SHA-256 `8cf3f6b5fa3ec835e491fff668341354dd6633a87beca0f2817ea1b406c73bc0` and ZIP CRC passed.

GitHub also contains a separately authored portable script `scripts/c2_four_ba_daily_peak_p95_mean_source_qa.py` which implements the same method. The local success **does not establish that exact Github script passed independent CI**.

## Scientific admission decision

- **Pass:** actual source-provenance and full-day consistency for this exploratory target robustness diagnostic.
- **Conditional:** retain raw daily peak as original primary descriptive pressure and add intra-day P95 as robustness co-outcome; add daily mean as distinct system demand metric, not substitute.
- **Blocked:** final daily-climate regression coefficients, operator-certification of AZPS/SRP high-spike records, fixed-vintage EIA930 cross-check for missing 2020 API, historical BA meteorological geographic masks, real FERC714 respondent 21 hourly data, trained climate attribution and CMIP6 SSP/PyPSA scenario results.

**C-1 untouched and frozen. C-2 descriptive QA only.**
