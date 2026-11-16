# C-2 E1 — Actual ERA5 A/B/C spatial-exposure classification of four-hour hot runs

Date: 2026-11-15. **Verified four-day source-only experiment, not observed electric grid stress. C-1 frozen.**

## Independently verified real input
Successfully archived Google ARCO ERA5, GitHub Actions run [43666836001](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43666836001), artifact 14143156157. Frozen CSV `REAL_ERA5_ABC_FOUR_DAYS_384_BA_HOURS.csv` SHA-256 `9ebeb843f3364d6e6726844253934a34fdc6acac0c4627c17ec207e8105cb179`.

An independent Python analysis re-ingested **384 actual matched BA/UTC hour rows**, verified all timestamps exactly equal four full UTC days (2023 Jan 15, Jul 1; 2025 Jan 15, Jul 1), 24 hours × 4 BAs per day, source SHA, all three A/B/C source temperature differences, valid finite temperature values, and `historical_BA_geography_approved=False`, `population_is_customer_weights=False`, `training_permitted=False`.

A: HIFLD 2018 area proxy; B: 2024 TIGER whole-county area proxy; C: 2020 Census estimates-base resident population proxy. **None represents validated BA electricity load location**.

## New continuity-sensitive output

For each BA/day/temperature threshold, calculate the longest contiguous sequence of ≥25°C, ≥30°C or ≥35°C proxy temperature **within that UTC day**. The illustrative *four-hour hot-day label* is whether longest run ≥4 hours. Counts refer to **four deliberately sampled days**, not a climatological event frequency.

| BA | Temperature cutoff | Days with a ≥4h run (A) | (B) | (C) | Days where masks disagree on run label |
|---|---:|---:|---:|---:|---:|
| AZPS | 35°C | 2/4 | 1/4 | 2/4 | **1** |
| BPAT | 25°C | 2/4 | 2/4 | 1/4 | **1** |
| CISO | 30°C | 2/4 | 2/4 | 1/4 | **1** |
| SRP | 35°C | 2/4 | 2/4 | 2/4 | 0 |

Source example at 2025-07-01 (24 consecutive UTC hours): AZPS 35°C longest runs A=**5 h**, B=**2 h**, C=**7 h**; CISO 30°C A=**4 h**, B=**4 h**, C=**0 h**. At 2023-07-01 BPAT 25°C longest runs A=**5 h**, B=**5 h**, C=**2 h**.

For independent consistency with prior *hourly* classification, A/B/C disagreement is AZPS 35°C **18/96** source hours, BPAT 25°C **9/96**, CISO 30°C **11/96**, and SRP 35°C **5/96**. A/B/C differ only in geography and weights, while ERA5 data source and UTC times remain fixed.

## Reproduction, safeguards and limitations

Source-only Python reproducer and four **passing local synthetic/source regression tests**, plus complete 48 BA-day/threshold run table, 12 BA/threshold summary, SHA256 source manifest and report are packaged in `C2_ABC_REAL_ERA5_4H_HEAT_RUNS_20261115.zip`, sha256 `5abddf968f5a3802ea0f615d35cd6340deab698df589b0629fb232a7a11fced5`. Github reproducer: `src/c2_abc_real_era5_four_day_heat_run_sensitivity.py`; prior `src/c2_era5_abc_heat_threshold_disagreement.py` was also hardened to demand exact BA/UTC coverage, pinned source CSV hash, finite original source temperatures and all three original difference checks. GitHub CI for new commits **has not been separately verified successful**.

**Methodological limitations:** Four selected days per BA, not independent random weather events; no inferential p-values or six-year hot-spell counts. Midnight UTC boundaries can truncate actual runs and *these are not locally defined heatwaves*. Temperature thresholds are illustrative, not fitted electric-demand stress thresholds. The archive's 2025 weather samples were already present in earlier geography sensitivity experiments; sealed 2024–2025 **demand test was not read** for this analysis. No model fit, climate attribution, grid stress, weather normalization or load-weighted geography validation is implied. Model admission remains BLOCKED, C-1 frozen.
