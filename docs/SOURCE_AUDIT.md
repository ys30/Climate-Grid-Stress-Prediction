# Phase-1 C-1 reusability and data audit — 2026-11-12

## Immutable starting point
- C-1 GitHub repo: https://github.com/ys30/Climate-Grid-Resilience-Research
- Frozen SHA: `6b549a6612f280646389f87bfc35453dd0e5d7dc` (freeze commit Nov 10 2026).
- Observed: 864 committed files, 164 GitHub workflows, 295 source files, 208 tests; basic CI success at https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42924877211 .
- Repository has only six small CSV examples/reference files; four of these are synthetic. Historical full hourly input *bytes are not in Git tree*. Historical outputs remain within historical CI artifacts/external sources, and need separate retrieval, hash/checks and durable preservation. Existence of scripts is NOT evidence of an accessible longitudinal panel.

## Reuse decision
| C-1 component | Reuse | Reason / guard |
|---|---|---|
| `src/grid_resilience/eia930_hourly_demand.py` | Adapt with attribution | EIA-930 hour-ending to UTC interval-start, unique BA-hour checks, API pagination and no silent imputation. Validate source revisions and demand semantics. |
| `src/grid_resilience/era5_point_weather_intake.py` | Intake technique only | Four illustrative city-near points, NOT spatial BA weather or wind farm conditions. Replace spatial assignment and exposure weighting. |
| `src/grid_resilience/factorial_dispatch.py` | PyPSA engineering skeleton only | +4°C, 30% wind penalty, 0.012/°C load response, 30°C threshold, generic gas/wind fleet and illustrative links are assumptions, NOT estimated coefficients or network adequacy. |
| `src/grid_resilience/paperc_eia930_2023_2024_hourly_fuel_panel.py` | Source-schema quality patterns | Fuel taxonomy shifts and missing values; no imputation of blank wind/hydro/storage as zero. |
| `tests/`, `.github/workflows/ci.yml` | Patterns only | C-2 requires separate unit/data-contract/temporal-leakage and solver CI. |
| Paper C E1-E3/96 scenarios/v13 | Citation and provenance only | No re-running or changing historical originals. |

## Public data assessment (availability is not downloaded/verified panel)
| Source | Resolution | C-2 use | Gate |
|---|---|---|---|
| EIA-930 | BA hourly | Reported demand, net generation and source-limited categories | Period coverage, revisions, BA changes, hour-ending UTC, fuel schema; do not treat interchange as physical transfer capacity |
| ERA5 / ERA5-Land | Hourly gridded | temperature, humidity, wind and solar drivers | grid selection, area/population/load weights, reproducible request/hash; meteorology not observed causal forcing by itself |
| EIA-860 | Annual | Generator inventory, additions/retirements | vintage-specific ID mapping; nameplate not available capacity |
| EIA-923 | Plant monthly/annual | Hydro/solar/wind generation totals and independent sanity checks | NOT hourly generator output ground truth |
| CAISO public OASIS/telemetry and hydro authorities | Varies | Separate observational evaluation | spatial/temporal coverage and copyright/source-vintage |
| NASA NEX-GDDP-CMIP6 | Daily 0.25° | Future scenario temperature/precipitation; wind/radiation only when available and verified | Bias adjustment, historical overlap, 24h disaggregation cannot be assumed accurate for hourly tails |

Official pointers: https://www.eia.gov/electricity/gridmonitor/ ; https://climate.copernicus.eu/climate-reanalysis ; https://www.eia.gov/electricity/data/eia923/ ; https://www.nasa.gov/ames/earth-science/nasa-earth-exchange-nex/gddp/downscaled-climate-projections-nex-gddp-cmip6/

**Next live data gate:** build a 2020–2025 EIA-930 × ERA5 BA-hour actual complete-case inventory before declaring eligible train/test years. If historic hourly technology-specific wind/solar/hydro observations cannot be reliably aligned, demote these to separate secondary outcomes, not pseudo-observations. Separate early years from test years; do not force historical climate trend attribution from only 2023/2024.
