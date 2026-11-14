# E1 repaired-geometry sensitivity and exploratory BA overlap gate — 2026-11-13

## Observed make_valid results (CI verified)
GitHub Actions success: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43540956239

| BA | Source topology | Make-valid polygonal candidate | Area relative to invalid raw projected-area calculation | Source YEAR |
|---|---|---:|---:|---:|
| AZPS | nested shells (invalid) | 127,829.910 km² | −0.000213% | 2018 |
| BPAT | nested shells (invalid) | 710,609.107 km² | −1.356627% | 2018 |
| CISO | ring self-intersection (invalid) | 331,717.778 km² | **−7.075822%** | 2018 |
| SRP | valid | 26,320.449 km² | 0% | 2018 |

These percentage changes are topology diagnostic comparisons against areas computed from originally invalid geometries. They are **not** scientific estimates of actual control-area boundary change, missing demand share, or uncertainty intervals. Each Shapely polygonal candidate is valid, but none has source-vintage, history, overlap, or modeling approval. The 7.08% CISO area discrepancy is particularly material and must be reviewed.

## Experimental grid weights, not modeling-admitted geography

New code: `src/c2_exploratory_grid_weights.py`, `tests/test_exploratory_grid_weights.py`, workflow `.github/workflows/e1-exploratory-grid-weights.yml`.

CI run: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43548795101. Initially queued; its completion and output still require explicit checking.

The workflow re-downloads the four source polygons, preserves the original, runs the Shapely topology repair **as a parallel derived candidate**, calculates 0.25° ERA5 grid-cell fractional overlap area in EPSG:5070, audits cell-weight sums and six BA-pair polygon intersections, and writes:

- `exploratory_BA_grid_weights_UNAPPROVED.csv`
- `overlap_sensitivity.csv`
- `exploratory_spatial_weight_audit.json`

Every record is labeled `exploratory_unapproved_geometry`, with explicit `weights_admitted_for_model: false`, `weather_data_fetched: false`, and `future_prediction_performed: false`. The historical ERA5-weather–demand joint panel remains **not yet built**.

## Priorities following numerical spatial QA
1. Read the grid-weight and overlap CI outputs. If it fails from expensive geometric intersections, build a spatial index/STRtree and calculate areas with prepared polygons, without changing the scientific interpretation.
2. Independently verify source polygon interpretation (control authority footprint versus EIA BA operating area), archival vintage, component/lake holes, shared/overlapping coverage and uncertainty from making invalid originals valid.
3. Keep data quality/vintage gate closed before model use. A strong source-based sensitivity plan might report two plausible boundary reconstructions and their impacts on region-weighted weather exposure, rather than claiming a single true boundary.
4. Once approved, obtain *real* hourly gridded ERA5 2m temperatures with explicit UTC observation convention; use existing `c2_era5_area_aggregate.py` + `c2_weather_join.py` with EIA demand QA flags.

No historical attribution, prediction skill, stress outcome, or CMIP6 future scenario results are implied.
