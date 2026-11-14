# C2 E1 — Confirmed HIFLD vs Census geospatial sensitivity: 8 real ERA5 hours

Evidence updated 2026-11-14. This is **Project C-2 only**; C-1 remains frozen.

## Verified genuine-source comparison

A = 2018 HIFLD source Control Area provisional topology-repair polygons. B = EIA-861/PUDL BA county membership × 2024 full-resolution Census TIGER county geometric union. Both are unapproved as EIA-930 balancing-area operating geographies, and the HIFLD/EIA-861 masks are **not** disjoint load geographies.

Matching hourly reanalysis source: public Google ARCO ERA5 0.25-degree, actual 2m Kelvin grid, all polygon-overlap cells weighted using EPSG:5070 projected intersection areas. **The comparison holds ERA5 timestamp, measurement, weighting formula and 0.25-degree grid definition identical, changing only mask geometry**. Each weight map sums to 1 per BA.

- First single-hour real ERA5 CI success https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43652340209
- Spatial polygon-overlap / area diagnostic success https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43652536420
- **Eight sampled real UTC-hour comparison CI success** https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43653861182
- Download 8-hour result CSV and provenance https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43653861182/artifacts/14137790469

Eight deliberately selected independent source times (all 12:00 UTC): Jan 15 and Jul 1 in 2020; Jan 15, Apr 1, Jul 1, Oct 1 in 2023; Jan 15 and Jul 1 in 2025. These 8 UTC points across years and seasons are a sparse designed sensitivity **sample**, not randomly selected independent days and not sufficient for a population causal or climatological estimate.

| BA | Min (B−A), °C | Max (B−A), °C | Median (B−A), °C | Negative / 8 samples |
|---|---:|---:|---:|---:|
| AZPS | −2.389686 | −0.952013 | **−1.676134** | **8** |
| BPAT | −0.114283 | +0.377621 | +0.078920 | 3 |
| CISO | −0.664241 | +0.035684 | −0.275308 | 6 |
| SRP | −2.321403 | −0.844639 | **−1.700573** | **8** |

The AZPS and SRP county-proxy candidate means are cooler than the HIFLD candidate for **all 8 sampled hours**. This is a **measured spatial-mask sensitivity of real ERA5 reanalysis**, not a demonstrated systematic historical temperature bias, not proof the county proxy is more correct, not a population-wide statistical test and not a load-demand elasticity.

Representative same-source single-hour comparison at 2023-07-01T12:00:00Z:
- AZPS A = 21.068864 °C, B = 19.521649 °C, B−A = −1.547215 °C.
- BPAT A = 14.177249 °C, B = 14.089404 °C, B−A = −0.087845 °C.
- CISO A = 20.475391 °C, B = 20.134971 °C, B−A = −0.340420 °C.
- SRP A = 25.425508 °C, B = 23.104105 °C, B−A = −2.321403 °C.

Source weights:
- HIFLD A candidate CSV SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.
- TIGER county B candidate CSV SHA256 `6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8`.

## Independent equal-area support diagnostics (NOT temperature)

| BA | HIFLD area km² | TIGER county area km² | Intersection km² | Jaccard |
|---|---:|---:|---:|---:|
| AZPS | 127,829.910 | 295,220.137 | 127,814.161 | 0.4329222 |
| BPAT | 710,609.107 | 729,344.449 | 691,002.852 | 0.9226279 |
| CISO | 331,717.778 | 437,721.013 | 331,712.912 | 0.7578097 |
| SRP | 26,320.449 | 50,234.135 | 26,316.787 | 0.5238444 |

County proxy contains nearly all HIFLD candidate area for AZPS/CISO/SRP, but also substantial additional space; that can plausibly change areal average meteorology. Do not treat near-containment as geographic correctness, because EPA documents BA jurisdictions are not strictly mappable to exclusive territory.

## Follow-up 24-hour diurnal sensitivity

Code `src/c2_era5_AB_24hour_sensitivity.py` and workflow https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654020965 analyze four 24-hour real source days:
2023 Jan 15; 2023 Jul 1; 2025 Jan 15; 2025 Jul 1. Four BAs × 24 hours × four sampled days = 384 planned BA-hour comparisons. **At report creation the new CI is still running; no 24-hour results are verified yet.**

## Scientific admission remains CLOSED

The independent 2024 Census county geometry represents county membership proxy, not verified 2020–2025 operating BA masks. No validated BA population/customer/load-weighted weather exposure has been calculated. HIFLD raw source topology repair and AZPS/SRP overlapping territories remain. No 2020–2025 B full six-year weather panel, weather-demand regression, GAM/XGBoost, anthropogenic ALL/NAT attribution, SSP future climate scenarios or PyPSA stress simulations were performed as part of this A/B sensitivity study.

To proceed to a publishable robust geographical conclusion, compare full diurnal profiles and then wider sampled windows or longer seasonal windows, freeze temporally appropriate source geography provenance, and document which spatial exposure estimand serves the inferential task. Do not switch model geography approval to true based only on a consistent temperature difference.

C-1 remains untouched.


## Confirmed 96-hour matched-day geographic sensitivity (four 24-hour days)

Independent actual ERA5 source CI **SUCCESS** for all four full-day jobs:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654020965 .

The all-hour per-day source results are preserved separately:
- 2023 winter Jan 15: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654020965/artifacts/14136897696
- 2023 summer Jul 1: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654020965/artifacts/14137810602
- 2025 winter Jan 15: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654020965/artifacts/14137436638
- 2025 summer Jul 1: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654020965/artifacts/14137656160

Separate strict re-ingestion and aggregation CI also **SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654203600 . The archived resulting 384-row CSV/summary/provenance is:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43654203600/artifacts/14137910200 .
Outer artifact SHA256 = `0a5e8bf688a38e83a3339389f48d0913179deb1eed3e39805fbeaabcf7a1dcaa`.

The actual four days are **2023-01-15, 2023-07-01, 2025-01-15 and 2025-07-01**. The source matched all 24 UTC hours under both original unapproved area-weight maps on each day; total four BAs × 96 source hours = **384 BA-hour spatial comparisons**. Both masks always use the same exact real public ARCO ERA5 2m temperatures and resolution.

| BA | 96-hour mean B−A, °C | Median B−A, °C | Min B−A, °C | Max B−A, °C | Hours B colder than A |
|---|---:|---:|---:|---:|---:|
| AZPS | **−1.921391** | −1.934339 | −2.926157 | −1.212622 | **96/96** |
| BPAT | +0.006933 | +0.020655 | −0.414651 | +0.347476 | 48/96 |
| CISO | −0.277619 | −0.291841 | −0.633558 | +0.139007 | 81/96 |
| SRP | **−1.930985** | −2.089636 | −3.027294 | −0.793948 | **96/96** |

Four individual 24-hour daily mean B−A results (°C):

| BA | Jan 15 2023 | Jul 1 2023 | Jan 15 2025 | Jul 1 2025 |
|---|---:|---:|---:|---:|
| AZPS | −1.589260 | −1.592199 | −2.343165 | −2.160942 |
| BPAT | +0.188705 | −0.220558 | +0.248510 | −0.188926 |
| CISO | −0.332365 | −0.393090 | −0.390118 | +0.005096 |
| SRP | −1.630599 | −1.869726 | −1.974800 | −2.248813 |

**Interpretation:** Candidate weather exposures for AZPS/SRP are meaningfully sensitive to polygon definition and showed a consistently cooler Census county proxy in each sampled source-hour. BPAT is comparatively insensitive in overall mean, with *seasonal sign reversal*. These four selected days are **not** a randomly sampled, full 2020–2025 BA climatology or independent 96-day dataset. Adjacent UTC hours are autocorrelated; never calculate p-values pretending they are 96 independent draws. The differences may reflect geographic support, elevation/land fraction and spatial weighting—not proven source error or historical temperature bias. The Census proxy does NOT automatically become the official or preferable BA electricity demand exposure.

This evidence reinforces the need for an explicit geographic exposure estimand and sensitivity plan before any EIA-930 weather-demand predictive experiments. `model_training_permitted=False` for both masks and all 384 records.
