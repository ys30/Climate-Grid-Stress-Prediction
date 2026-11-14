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
