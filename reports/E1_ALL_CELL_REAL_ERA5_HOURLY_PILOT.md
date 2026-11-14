# C2 E1 real ARCO ERA5 all-cell four-BA one-hour pilot — 2026-11-13

## Prior CI-confirmed prerequisites
- Six-year EIA-930 source coverage and 2023/2024 exact missingness QA succeeded.
- National 2018-vintage candidate BA polygons sourced and stored with full provenance.
- Original BPAT, CISO, AZPS source polygons invalid; exploratory Shapely make_valid candidates valid, but model-use **NOT approved**.
- Four BA gridded cell intersection weights from real source candidates successfully computed: AZPS 265, BPAT 1557, CISO 662, SRP 55 cells. See https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43548907152 .
- True ARCO ERA5 2m Kelvin gridded source access verified at 12 individual cells, https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43549940516. The 12-cell sample is not a BA area mean.

## Full-cell one-hour empirical attempt
New script `src/c2_era5_full_grid_one_hour.py` and workflow:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43553846440 .

The workflow retrieves the **frozen** unapproved area weights artifact from the verified prior successful run, queries ARCO ERA5 only at UTC `2023-07-01T12:00:00Z` and the bounded multi-BA western US grid extent, verifies exact 0.25° grid cell coordinates, converts Kelvin to Celsius and calculates one **exploratory** weighted 2m temperature per BA using **all** its candidate polygon-intersected grid cells. Outputs use explicit `historical_weather_exposure_approved: false`, no model fit, no attribution, no weather–demand join.

At writing time this actual-source all-cell CI job had been queued; no successful all-cell weather measurement was yet verified. A passing isolated unit test alone is not proof of real-data access.

## Geographic interpretation and critical limits
- The source candidate polygons are from `YEAR=2018`; dynamic 2020–2025 BA footprints not independently demonstrated.
- AZPS/SRP candidate intersection ≈25,441.575 km² (96.66087% of SRP area). The two electric load series are separate BA data products, and weather exposures from overlapping polygons must not be interpreted as mutually exclusive partitions.
- CISO make_valid area differs by about 7.08% from invalid source area calculation: topology sensitivity, not proven physical boundary change.
- The final `src/c2_ba_era5_weights.py` requires explicit source-vintage, overlap, topology repair and exposure interpretation review references; unreviewed source polygons fail model admission.
- An exploratory single UTC hour is **not** a six-year weather exposure panel, and cannot provide an out-of-sample XGBoost/GAM score, causal anthropogenic climate attribution, or CMIP6 scenario grid-stress outcome.

## Next scientific milestones
1. Verify real all-grid one-hour CI and inspect data gaps, cell counts and source metadata.
2. Bound a continuous 24-hour source sample; verify time regularity and compare area-weighted thermodynamic exposures with source candidate geometry sensitivity.
3. Resolve source polygon vintage and overlapping coverage scientifically (or use alternative independently audited exposure estimands). Build signed and hashed BA geometry crosswalk before admitting final model weights.
4. Stream/cache 2020–2025 hourly ERA5 2m gridded subsets in reproducible chunks; recheck UTC alignment with EIA-930 and quarantine flags.
5. Only then benchmark calendar / GAM / XGBoost with train 2020–2022, val 2023, held-out 2024–2025, and investigate future CMIP6 SSP scenarios.

## CI-verified result: real complete source area-weight hour

The actual-source single-hour CI `43553846440` **passed**, using 5,472 loaded ARCO ERA5 grid coordinates in the Western U.S. bounding rectangle. At UTC 2023-07-01T12:00:00Z, the source grid supported all source-derived grid-cell weights for each BA. The **experimental** polygon-area-weighted temperatures were:

| BA | Actual intersected cells | Exploratory full-cell 2m temperature (°C) |
|---|---:|---:|
| AZPS | 265 | 21.068864 |
| BPAT | 1557 | 14.177249 |
| CISO | 662 | 20.475391 |
| SRP | 55 | 25.425508 |

Observed gridded Kelvin values were finite in all selected cells. The grid data source is the real public ARCO ERA5 0.25° archive, and frozen input area-weight CSV SHA-256 is `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.

**Publication caution:** the numeric weather values are real ERA5 observations; **the choice of BA geographic mask and statistical area-weighted estimand remain provisional**, since original 2018 HIFLD control-area polygons required make_valid, CISO repair differed by ~7.08% from invalid raw area arithmetic, and AZPS/SRP candidate footprints overlap by 96.66% of SRP.

## Next bounded 24-hour experiment

`src/c2_era5_24h_exploratory.py`, `tests/test_era5_24h_exploratory.py`, and `e1-real-24h-exposures.yml` now attempt a contiguous 24-hour real Zarr weather subgrid, validating all 24 UTC hour stamps and all four BA grid exposures for each hour. GitHub CI: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43553993546. At document creation, CI result not yet verified. Expected result if successful: 96 rows, NOT an approved historical weather-demand panel.


## CI-verified contiguous 24-hour actual ARCO observations

CI **success**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43553993546 .

All 24 UTC hours on **2023-07-01** were present and continuous, bounded weather-source rectangle = 5,472 0.25-degree grid cells per hour, with each BA using its complete candidate polygon-weighted cell set. Total exactly **96** candidate-geography BA temperature rows. Daily minimum–maximum of hourly BA-mean temperature (°C):
- AZPS: 21.068864 to 38.536893.
- BPAT: 14.177249 to 28.330700.
- CISO: 20.475391 to 35.619391.
- SRP: 25.425508 to 42.324877.

No grid-value imputation. These are actual ERA5 cell observations, but the regional exposure spatial estimator remains **UNAPPROVED**.

## Actual hourly EIA-930 and ERA5 diagnostic alignment

CI **success**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43554151147 .

This downloaded and reconciled official 2022 H2 and 2023 H1/H2 EIA-930 source CSVs, applied the existing exact-hour EIA demand-quality flags, and paired them with the frozen **real** 24-hour ERA5 exploratory exposure source artifact:
- Exactly **96** exact UTC hourly demand/weather pairs for four BAs, 2023-07-01.
- **Zero** EIA source anomaly flags among those 96 observations under the existing conservative candidate screen.
- No missing weather or load hours, no interpolation, no model fit.
- Raw EIA-930 demand MW within the selected day: AZPS 3438–6776, BPAT 5188–7785, CISO 23082–35566, SRP 3177–7054.
- Output artifact: `24h_REAL_SOURCE_UTC_PAIRED_NOT_MODEL.csv`, and `real_24h_pairing_manifest.json`.
- `candidate_geography_approved=False`, `model_training_eligible=False` for every row; **not a model-ready panel**.

## Model-use safety regression

`src/c2_weather_join.py` now requires explicit per-weather-record `geometry_approved=True` and nonblank `geometry_admission_id` for model-ready complete-case joins. `tests/test_weather_join.py` rejects unapproved or missing admission identifiers; experimental 24h source observations cannot enter the approved join by default. Actual independent scientific sign-off of 2018-vintage candidate BA boundaries, AZPS/SRP high overlap and 7.08% CISO repair diagnostic still missing.

**End-to-end evidence achieved:** official EIA-930 raw demand → verified UTC source reconciliation + quarantine flags; public ARCO ERA5 → all-source-cell weighted hourly meteorology; diagnostic exact UTC pairing. **Not yet achieved:** independent historical BA source approval, 2020–2025 panel, calendar/GAM/XGBoost held-out skill, ALL/NAT anthropogenic attribution, SSP future grid stress.
