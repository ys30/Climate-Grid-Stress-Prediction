# C2 E1 — real January + July source weather-demand audit, 2020–2025

Last verification: 2026-11-14, CI evidence below.

## Genuine empirical data completed

This is an independently verified *public-source data engineering* milestone, not trained or scientifically approved weather-demand modeling. We retrieved genuine ARCO ERA5 2m hourly weather for all source-derived weighted grid cells within four provisional Control Area masks (AZPS, BPAT, CISO, SRP), used their full 0.25° grid overlap weights, and aligned to original UTC-start EIA-930 demand for all 31 days of January and July in each of 2020, 2021, 2022, 2023, 2024, and 2025.

- January source CI, all six jobs success: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43619234662
- July source CI 2020 and 2025: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563497776
- July source CI 2021–2024: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563639298
- **12-month-source reconciliation CI success**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43619521745
- Download consolidated QA CSV and manifest: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43619521745/artifacts/14123767173 . Artifact ZIP digest SHA256 `9bdfad88497a906d3407358e86bcfae4f188d28f5d0b97e294c167a9d42c6b3f`.

Each month has 744 unique UTC hours × 4 BAs = 2,976 real ERA5 observations. Exactly twelve months across the six years (January+July), **not twelve months each year**.

| Year | January actual source pairs | January EIA demand missing | January source anomaly candidate flags | July actual source pairs | July EIA missing | July candidate flags |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 2,976 | 0 | 3 | 2,952 | 24 | 0 |
| 2021 | 2,976 | 0 | 0 | 2,976 | 0 | 1 |
| 2022 | 2,975 | 1 | 0 | 2,976 | 0 | 3 |
| 2023 | 2,976 | 0 | 4 | 2,976 | 0 | 3 |
| 2024 | 2,976 | 0 | 0 | 2,976 | 0 | 0 |
| 2025 | 2,975 | 1 | 0 | 2,974 | 2 | 2 |
| **Total** | **17,854** | **2** | **7** | **17,830** | **26** | **9** |

Overall from 12 selected true-source months: **35,712 / 35,712 actual ERA5 candidate BA-temperature hours; 35,684 original EIA × weather nonmissing pairs; 28 original EIA missing BA-hours; 16 source anomaly *candidate* flags.** Anomalies are not automatically proven errors, nor are all nonmissing pairs automatically approved training data.

## All observed missing demand evidence (no imputation)

- CISO, 2022-01-05T09:00:00Z (1 hour).
- SRP, 2025-01-23T07:00:00Z (1 hour).
- SRP, 2020-07-11T07:00:00Z through 2020-07-12T06:00:00Z (24 hours).
- SRP, 2025-07-07T06:00:00Z and 2025-07-10T07:00:00Z (2 separate hours).

The missingness is limited to the 12 audited months. It must not be extrapolated to other months/years. Full-series EIA-930 coverage and E0 candidate quarantine are independent quality controls.

## Experimental spatial geography must not be used as vetted history

The countrywide source `Control_Areas` polygon features carry YEAR=2018, while modeling would span 2020–2025. Three original polygon topologies were invalid; Shapely make_valid diagnostics shifted CISO raw-area calculation by ~7.08%, and derived AZPS/SRP source areas overlap by ~96.66% of SRP area. Spatial weighting is **exploratory** and does not itself establish historical BA reporting area, load-weighted exposure, or causal impact. The frozen area-weight source CSV SHA256 used by all 12 months is `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.

`c2_weather_join.py` requires documented approval ID for model-ready data. `c2_temporal_gate.py` no longer treats E0 source coverage as actual training approval. The twelve month source reconciliation flags `all_12_months_each_year_verified=false`, `historical_BA_geography_approved=false`, and `training_permitted=false`.

## Next scientific gating work

1. Obtain an independent and temporally appropriate BA boundary definition, distinguish overlapping service territories from EIA BA operating areas, review geometry and verify crosswalk with source provenance; add alternate weather estimands for sensitivity.
2. Stream/cache additional real ERA5 months for 2020–2025 with nightly/seasonal source availability checks, immutable source hashes and no automatic infilling of EIA BA-hour missingness.
3. Identify the 16 anomaly *candidates* by source timestamp/value, review EIA's original reporting/handling conventions, distinguish impossible values from spikes or special reporting.
4. Once full weather panel and geography/quality are approved, execute chronological predictive baselines, GAM/XGBoost (2020–2022 train; 2023 validation; 2024–2025 untouched holdout). Historical weather association alone cannot prove anthropogenic climate-change effects without independent ALL versus NAT forcing counterfactual.
5. CMIP6 SSP forcing and downstream PyPSA operations simulations remain future stage, not accomplished in E1.

**C-1 remains frozen and unchanged. This report concerns C-2 only.**
