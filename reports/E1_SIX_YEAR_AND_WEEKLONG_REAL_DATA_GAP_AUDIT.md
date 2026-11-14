# E1 six-year real-data audit and seven-day source gaps — 2026-11-13

## Verified six-year 48-hour source windows

Workflow: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43555573681 (all six years succeeded). Reconciliation: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43561884994 (SUCCESS; https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43561884994/artifacts/14100666858).

2020–2025 each contributed 48 hours per BA on July 1–2, totaling 1,152 complete real ARCO-ERA5 × EIA-930 BA-hour source pairs out of 1,152 sampled slots. The same frozen candidate BA geography weights were used throughout (SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`). No observed demand imputation or ERA5 interpolation. The source candidate anomaly rule flagged zero hours within those *sampled windows*.

**This does not establish full-year completeness.** Original nationwide source control area polygons carry YEAR=2018 and were repaired as candidate geometries, not validated as 2020–2025 historical service territories. The result must not enter training or attribution.

## Verified seven-day extension: actual source missingness matters

Final CI: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43562198127; all three independent jobs completed SUCCESS after missing-demand diagnostic support was added.

| Year | Period | Full observed weather hours | Actual paired demand and weather hours | Original demand missing | Outcome |
|---|---|---:|---:|---:|---|
| 2020 | July 1–7 UTC | 672 | 672 | 0 | success |
| 2024 | July 1–7 UTC | 672 | 672 | 0 | success |
| 2025 | July 1–7 UTC | 672 | **671** | **1** | success with explicitly recorded gap |

The 2025 missing original EIA-930 BA-hour was **SRP at 2025-07-07T06:00:00Z**. ERA5 did not lack the corresponding source hour. The audit now creates a null original demand row and a distinct `REAL_EIA930_MISSING_DEMAND_EPISODES.csv` (no filling/interpolation); every record remains `train_or_validate_eligible=False`. Audited seven-day windows total 2,016 BA-hour *slots*, 2,016 real weather measurements and **2,015 complete demand-weather pairs**.

Archived CI artifacts:
- 2020: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43562198127/artifacts/14100717533
- 2024: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43562198127/artifacts/14100587583
- 2025: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43562198127/artifacts/14101300289

## Corrected model-use admission policy

Old E0 `c2_temporal_gate.py` printed misleading `empirical_model_training_permitted=True` when coverage alone passed. Fixed: E0 emits a *coverage-only* boolean `coverage_only_source_gate_passed` while `empirical_model_training_permitted=False` until independent full ERA5 observations, source anomaly QA, and vetted geographies are approved. New test ensures even 100% EIA annual coverage never authorizes model training.

Source gap audit `src/c2_era5_seasonal_source_audit.py` now supports `--allow-source-gaps`, but no missing source hour is filled or mislabeled complete. Its default remains strict: absence of raw demand fails exact source pairing.

The E0 annual coverage CI originally ran the full expanding test suite without installing new geospatial/numeric dependencies and consequently failed; updated `.github/workflows/e0-yearly-coverage.yml` installs numpy, xarray, shapely and pyproj before tests. Its new run must be checked independently before claiming E0 regression green.

## Research limitations and next blockers
- E1 has CI-verified 6-year **seasonal samples**, NOT 2020–2025 full-hour meteorological panel.
- Spatial estimates use 2018-vintage national Control Areas candidates, with CISO geometry repair area diagnostic ≈7.08% and AZPS/SRP polygonal overlap ≈96.66% of candidate SRP. Source admissibility remains **closed**.
- No calendar/GAM/XGBoost model trained; no estimates of anthropogenic climate-change attribution; no future SSP / PyPSA stress outcomes.
- Next tasks: independent historic-BA geography review and uncertainty analysis, then full-month/year real ERA5 streaming with immutable provenance and source-gap exclusions before predictive weather sensitivity or scenario comparison.
