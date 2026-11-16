# Project C-2 E1 — Actual ERA5 spatial-proxy heat-hour classification sensitivity

Date: 2026-11-15. **Real-source descriptive geographic uncertainty evidence; not actual grid stress or a fitted demand model. C-1 remains frozen.**

## Independently rerun evidence

Actual prior successful [GitHub Actions source run 43666836001](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43666836001), archived artifact 14143156157, ZIP SHA256 `6510fef8e749a044c0ccc874a53db8afb671dd923f8269283d077562c5002598`. The independently pre-verified 384-record CSV source SHA256 is `9ebeb843f3364d6e6726844253934a34fdc6acac0c4627c17ec207e8105cb179`.

Data: four balancing authorities (AZPS/BPAT/CISO/SRP); four intentionally selected complete 24-hour UTC days (2023-01-15, 2023-07-01, 2025-01-15, 2025-07-01); 96 matched genuine ARCO ERA5 BA-hours per BA. Exposures: A = HIFLD 2018 area, B = TIGER county 2024 area, C = Census 2020 estimates-base county population weight. **All A/B/C are unapproved historical electricity load exposure proxies.**

For each exact BA/UTC time, apply fixed illustrative thresholds 25, 30 and 35 °C separately to A/B/C temperatures. Count an hour as **classification disagreement** when at least one geography proxy is >= cutoff and at least one is below. Disagreement is counted **once per BA-hour**. These cutoffs are not calibrated electricity-load or physical stress thresholds.

## Actual 96-hour results

| BA | Cutoff °C | A hot hours | B hot hours | C hot hours | Disagreement hours/96 |
|---|---:|---:|---:|---:|---:|
| AZPS | 25 | 41 | 36 | 44 | 8 |
| AZPS | 30 | 30 | 24 | 36 | 12 |
| AZPS | 35 | 17 | 7 | 25 | **18** |
| BPAT | 25 | 20 | 20 | 11 | 9 |
| BPAT | 30 | 5 | 5 | 0 | 5 |
| BPAT | 35 | 0 | 0 | 0 | 0 |
| CISO | 25 | 28 | 27 | 21 | 7 |
| CISO | 30 | 16 | 15 | 5 | **11** |
| CISO | 35 | 2 | 2 | 0 | 2 |
| SRP | 25 | 48 | 43 | 48 | 5 |
| SRP | 30 | 41 | 36 | 41 | 5 |
| SRP | 35 | 28 | 23 | 28 | 5 |

Most conspicuous classification disagreement: **AZPS at 35°C, 18 of 96 actual sampled hours (18.75%)**, reflecting different polygon / resident population area exposure. Also **CISO at 30°C, 11 of 96 actual hours (11.46%)**. Because all three exposures use the exact same ERA5 grid/time at each hour, the source comparison isolates *geographic support/weighting sensitivity* in the 2023/2025 selected time windows.

## Source constraints, reproducibility and limitations

A real local Python re-ingestion independently checked all 384 distinct BA-hour records, the four selected dates, 96 hours/BA, existing difference arithmetic, and all historical-approval/model-training fields `False`. Outputs: 12-row BA/cutoff summary, **48-row BA/day/cutoff table**, **1,152-row hour/cutoff classification table**, JSON provenance and Python reproduction script, packaged in `C2_ERA5_ABC_HEAT_THRESHOLD_DISAGREEMENT_20261115.zip` (ZIP SHA256 `5e3cf5d214405f431af95b1bde13d3f25ced59e79a200169dbf6ede467bda4e8`). Separate compact GitHub reproduction code: `src/c2_era5_abc_heat_threshold_disagreement.py`, commit `9c4162788ab0ed7dea4e68396123c901a5c0624b`.

These **four selected UTC dates** are not an unbiased annual sample. Adjacent hourly classifications are autocorrelated; there are no independent daily p-values, full-climatology probability estimates, or weather-model predictive skill claims here. The 2025 ERA5 descriptive weather sample was already used in source proxy analysis, but **sealed 2024–2025 demand test observations were not used in threshold selection or model fitting**. A hot ERA5 proxy hour is not evidence that the BA actually experienced an electricity peak or grid failure. The large differences do not tell us which mask best represents BA demand: Census resident-population weights are not electric meter / demand weights.

## Consequence for the manuscript

This provides a more operationally interpretable **Spatial Exposure Definition Sensitivity** result: geographic uncertainty changes even the binary classification of potential heat-exposure hours, not merely the continuous proxy mean temperature. It is suitable as a **methodological sensitivity** table/figure, not as a main climate impact attribution or actual grid stress result.

Still blocked: `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, and `LOAD_QUALITY_HOLDOUT_PROTOCOL`. `model_training_permitted=false`. Independent PUDL/EIA-930 historical source-vintage value comparison still lacks verified real 3-ZIP execution output.
