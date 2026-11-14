# C2 E1: CI-verified exploratory four-BA grid weights and overlap; live sampled ERA5 pilot

## Verified computation (2026-11-13/14 UTC)
Successful real-source-geography geometry sensitivity workflow: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43548907152

Based on national Control Areas source geometries (YEAR=2018), derived with Shapely make_valid; full 0.25° grid overlap areas and weights were computed for all four regions. This **does not authorize historical BA geometry**.

| BA | Intersected ERA5 0.25° cells | Derived candidate area km² | Weight sum |
|---|---:|---:|---:|
| AZPS | 265 | 127829.910 | ≈1 |
| BPAT | 1557 | 710609.107 | ≈1 |
| CISO | 662 | 331717.778 | ≈1 |
| SRP | 55 | 26320.449 | ≈1 |

## Pairwise source geography overlap

**AZPS ∩ SRP = 25,441.575 km²**, or **19.90268% of AZPS candidate and 96.66087% of SRP candidate**. AZPS ∩ CISO small ≈0.1 km² (round-off/topology boundary sensitivity), all other pairs ≈0 km² in same workflow.

It is **not justified** to infer AZPS and SRP are geographically disjoint. Yet overlapping BA weather-region exposures can be correlated and need not themselves indicate a double-counted load: they are separate BA-hour demand series and have independently scoped reporting territories. Do not add the four BA areas or sum exposure weights across BAs as if partitioning the Western grid; do not infer nonoverlapping asset footprints.

The heavy source polygon intersection initially failed because projecting a complex polygon before clipping caused a GEOS topology conflict. The corrected implementation clips valid geographic geometries to each 0.25° cell, then transforms each clipped component to equal-area EPSG:5070 for its area; successful workflow verified numeric weights.

## Geographic admissibility remains blocked

- National source polygon YEAR=2018, not validated for each 2020–2025 reporting year.
- CISO make_valid candidate differs in raw computed polygon area by ≈7.08%, a diagnostic rather than a known factual change.
- AZPS and SRP candidates overlap substantially: evaluate service-area/BA reporting-area distinctions, and test boundary/weight uncertainty before any claim about region-wide demand elasticity.
- Neither area-weighted ERA5 observational weather data for the whole four-BA territory nor ML models have been fit.

## Actual weather data next action

The independent earlier ARCO ERA5 *single-cell* source smoke test succeeded. A new source-linked **12-grid-cell weather access pilot** now reads the *frozen derived candidate grid-weight artifact* from GitHub Actions run 43548907152, selects the 3 highest-weight 0.25° cells for each BA, fetches actual 2023-07-01T12:00Z ERA5 temperature and saves a provenance file.

Pilot CI: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43549940516. At this document creation, CI completion not yet verified.

**These 3 selected cells per BA are emphatically NOT a substitute for the full 55–1557 cells per BA, and cannot be used for prediction training, BA-area averages or causal attribution.** Once the pilot succeeds, next steps are versioned ERA5 regional 0.25° hourly subset acquisition and historical geometry uncertainty adjudication.


## Verified 12 real ERA5 grid-cell records (subsequent CI SUCCESS)

Successful source data run https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43549940516. It used archived *experimental* area-weight artifact from successful 43548907152 (weight CSV SHA-256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`), and queried actual `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`.

Timestamp 2023-07-01T12:00:00Z:

| BA | Latitudes (°N) | Longitudes (0–360°E) | Actual individual ERA5 2m temperature (°C) |
|---|---|---|---|
| AZPS | 31.75,31.75,32.00 | 248.25,248.50,247.75 | 23.58938,22.50421,23.69497 |
| BPAT | 40.25,40.25,40.25 | 245.25,245.00,245.50 | 13.39669,14.17489,13.16403 |
| CISO | 32.75,32.75,32.75 | 243.25,243.50,243.75 | 18.20464,22.06234,22.05648 |
| SRP | 32.75,32.75,32.75 | 247.00,247.50,247.25 | 28.10598,26.87222,27.48812 |

The tested request matched 12 individual indexed ERA5 grid cells, with original weights retained. These are *not* the full-area-weighted BA temperatures. The 3 largest individual weights per BA sum to only ≈1.54% AZPS, ≈0.249% BPAT, ≈0.587% CISO and ≈7.404% SRP of their respective total BA area weights. Selecting 3 top cells is insufficient for valid BA-area exposure and cannot support any climate-impact effect estimate.

## Model-admission safeguards

The official `src/c2_ba_era5_weights.py` path now requires four explicit `True` independently reviewed statuses and four nonempty review evidence references:
- historical source-vintage applicability to 2020–2025;
- spatial overlap interpretations for the AZPS/SRP near-containment;
- `make_valid` topology repair methodology;
- the estimand: BA area-weighted meteorology versus load-weighted electricity demand.

`tests/test_ba_geography_admission.py` specifically refuses default/unreviewed candidate geometries. Its CI status must be checked separately; approval is **not** automatically inferred from unit tests. The exploratory artifact is kept independent.
