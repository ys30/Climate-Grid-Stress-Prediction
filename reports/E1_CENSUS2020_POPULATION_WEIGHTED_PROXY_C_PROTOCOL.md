# C2 E1 — Proxy C: Census 2020 population-weighted ERA5 geography (source-built, approval CLOSED)

Date: 2026-11-14 (Mountain Time). C-1 remains frozen; this work lives only in C-2.

## Why a third exposure definition is needed

Original real ARCO ERA5 × EIA930 data are complete for 72 calendar months in 2020–2025 as source-only observations: 210,432 ERA5 BA-hour candidates, 260 missing original BA-demand hours, 70 EIA930 source anomaly candidates; neither study-area mask was approved as an operational BA electricity demand footprint.

Two experimental weather exposures already empirically evaluated:
- A = 2018 HIFLD Control Areas repaired topology and area weighted ERA5, SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.
- B = year-specific EIA-861/PUDL BA-to-county membership, fixed 2024 unsimplified TIGER county unions and area weighted ERA5, SHA256 `6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8`.

Four actual complete months of A/B reanalysis comparisons in 2023 and 2025 are independently verified, total 11,904 BA-hour observations:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659771480/artifacts/14140205056 .

A vs B changes only spatial integration domain. The gap is large for AZPS and SRP; this motivates examining another defensible *approximate* spatial exposure.

## Proposed Proxy C definition — important distinction from actual customers

**Proxy C is NOT derived from observed electric customers or hourly kWh.**

Inputs:
1. Official US Census 2020 Decennial PL 94-171 (redistricting), total population **`P1_001N`** at county geography. Official documentation: https://www.census.gov/data/developers/data-sets/decennial-census/2020.html and https://api.census.gov/data/2020/dec/pl/groups/P1.html .
2. Frozen EIA-861/PUDL BA-to-county FIPS crosswalk for the four BAs. Source membership CSV SHA256 `6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68`; source archive https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43647297586/artifacts/14134338768 .
3. Official full-resolution Census TIGER 2024 national counties ZIP at https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip , verified earlier SHA256 `04e668d3502757c837c13444730547cd967f28a2c49aeffb873d1792ab2cb97b`.

For each selected county `c`, uniformly distribute its 2020 total population `P_c` over its fixed 2024 county geometry polygon. For every ERA5 grid cell `g` (0.25°), use true EPSG:5070 equal-area geometry overlap:

`M_(c,g) = P_c × Area(C_c ∩ G_g) / Area(C_c)`.

For each BA `b`, sum population mass `M_(b,g) = Σ_{c∈BA_b} M_(c,g)`; normalize grid weight `w_(b,g)=M_(b,g)/Σ_g M_(b,g)`. Candidate weather `T_(b,t)=Σ_g w_(b,g) ERA5_2m_(g,t)`.

Both overlapping BA county memberships and boundary-vintage mismatch are preserved; no artificial partition of overlapping AZPS/SRP counties. The calculation is area-uniform *within each county*; differences in within-county settlement, utility customers, building energy end-use, and demand location are unresolved.

### Model-use caveats

- Census P1 population is **total resident population**, not households, electric-meter accounts, annual kWh, peak load, or electricity customers.
- 2020 P1 totals are combined with 2024 TIGER geography as an explicit *cross-vintage proxy*; no claim of census-boundary contemporaneity for all six years.
- EIA-861 county BA membership is a county-level source proxy; electric grid operating BA territories are not guaranteed to be geographically exclusive.
- Population weights are normalized within each BA separately and may overlap; never use them to sum four BA demand without source BA crosswalk.
- Even if Proxy C succeeds and has sensible weights, **no automatic historical geography admission** is granted, and no final GAM/XGBoost/heldout test or anthropogenic climate attribution is authorized.

## Executable code and status

- Source weight builder: `src/c2_era5_population_county_weights.py`.
- Strict model-gate, FIPS, source-count, and normalization tests: `tests/test_era5_population_county_weights.py`.
- Public 2020 Census API + full TIGER/Line source builder CI: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43660687765 . A prior draft run https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43660654414 was also triggered.
- Four fixed UTC-hour ERA5 matched grid A/B/C comparison code: `src/c2_era5_three_proxy_comparison.py`.
- Conditional downstream A/B/C CI workflow `.github/workflows/e1-ERA5-three-proxy-A-B-C.yml` waits for Census proxy C workflow success and downloads its source artifact using triggering-run ID.

**At writing, Census source C GitHub jobs were QUEUED and no Census population values, C weights or real A/B/C temperature differences are yet verified.** If Census API requires a key or fails, treat the source as blocked and resolve its provenance rather than inventing population values or switching to a mislabeled substitute.

## Acceptance criteria

Pass only on verified original source population response and ZIP SHA256, complete required GEOID/FIPS matches, nonnegative integer P1 totals, valid county geometries, area conservation within 0.2% for each BA, all grid weights finite and positive, each BA sum exactly one, and all provenance/model flags false. For A/B/C temperature comparison, require actual public ERA5 Kelvin source on identical UTC times, exact 4 BA × 4 time records, all frozen source hashes and true correct ΔC−B/ΔC−A.

Next after verified C: compare real 4 UTC hourly readings across January and July in 2023/2025, then consider a longer C vs A/B independent sensitivity; do not call any of these a validated load-weighted weather indicator.

C-1 unchanged; formal C-2 model admission remains CLOSED.
