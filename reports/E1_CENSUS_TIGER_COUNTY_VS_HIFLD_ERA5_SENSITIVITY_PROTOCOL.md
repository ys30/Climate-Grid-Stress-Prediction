# C2 E1 — Census TIGER / EIA-861 BA county-proxy B versus HIFLD A

Date 2026-11-14. **PROTOCOL ONLY. Source workflows queued, no A/B numeric result yet.**

## Grounded study design

The six-year ARCO-ERA5 / EIA-930 actual-source archive covers 210432 BA-hour observations, but its BA weather masks are derived from *unapproved* 2018 national HIFLD Control Area polygons. We need an independent geography sensitivity experiment.

**A: HIFLD 2018 candidate.** The archive from GitHub run 43548907152 has full 0.25-degree ERA5 grid intersection weights. Its SHA256 is e4e0990cd47e8517d01731231eb4ed3da06649840c99c5b8cb3. Three original polygons needed source topology repair; AZPS and SRP overlap 96.66% of SRP area. It is not a verified BA electricity-load geography.

**B: Census TIGER 2024 / EIA-861 county proxy.** The independent actual PUDL BA-county annual membership crosswalk contains all 24 BA/year observations for 2020-2025: AZPS ID 803 / 15 counties; BPAT ID 1738 / 109 counties; CISO ID 2775 / 58 counties; SRP ID 16572 / 3 counties. All BA-to-county FIPS memberships were unchanged in the source observations from 2020–2025. **This stability is county-granularity only, not proof a BA operating footprint or legal service territory stayed unchanged.** Source artifact: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43647297586/artifacts/14134338768 .

County geometry for experiment B is the official **non-simplified** TIGER/Line 2024 national county shapefile:
https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip .
Documentation: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2024.html .
Census says the generalized Cartographic Boundary files are not intended for area/perimeter calculation: https://www.census.gov/programs-surveys/geography/technical-documentation/naming-convention/cartographic-boundary-file.html . This study therefore avoids the generalized 500k file.

## Methods and provenance commitments

- Download TIGER 2024 national county shapefile, save downloaded ZIP SHA-256 and exact FIPS crosswalk source hash.
- Match the selected 2024 EIA-861 county codes to county GEOID and union each BA's counties independently; do **not** erase overlapping county memberships. Explicitly retain geometry_approved=false and source_approved=false for all four BA unions.
- Calculate full 0.25-degree ERA5 grid-cell overlap weights, clipping in lon/lat first, then projecting clipped areas to EPSG:5070. Check every BA's weights sum to 1.
- For genuine ERA5 2m data at the *same 2023-07-01 12:00 UTC instant*, calculate the source-weighted spatial area temperature for A and B and report difference B minus A in Celsius for each BA.
- Fix the TIGER geometry year at 2024 and clearly label the resulting 2023 weather calculation as a fixed-vintage *proxy sensitivity*, **not validated 2023 BA territory**.
- Record both independent area-weight CSV hashes, sample source metadata and any missing weather grid cells. Avoid silent weather imputation or tuning B based on the demand test period.

Source geometry workflow: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43651609278 .
Real ARCO ERA5 A/B workflow: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43651727099 .

**At document creation both GitHub workflows were QUEUED. No numeric Celsius differences or successful TIGER construction are yet verified.** Do not treat CI source/artifacts as successfully produced until the jobs finish.

## Scientific admissibility

This is spatial input sensitivity, NOT a geography admission. EPA documents BAs do not have strict geographic footprints; EIA BA operating function and EIA-861 served-county proxies need not coincide. The BA weather exposure remains unapproved; historical 2020–2025 E1 source archive, original load gaps and anomaly candidates remain unchanged; neither the E2 predictive model, anthropogenic attribution nor E3 SSP/PyPSA runs are authorized.

C-1 is frozen and unchanged.


## 2026-11-14 execution audit — independent county source construction verified

**Actual Census TIGER geometry workflow SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43651609278 .

The source download actually retrieved `83,913,260` bytes of Census TIGER/Line 2024 county shapefile ZIP, SHA256 `04e668d3502757c837c13444730547cd967f28a2c49aeffb873d1792ab2cb97b`. Source EIA-861 county membership CSV SHA256 `6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68`. All 182 **distinct** county geometries required by the four BA union masks were actually found and validated; they cover the expected 15 AZPS, 109 BPAT, 58 CISO, 3 SRP original source county memberships (185 BA-county entries with 3 SRP/AZPS county repeats). Four union polygon geometries are valid. GeoJSON SHA256 `7f7cc843e3a6db958ad71a8dce5b98df882bb20bead0b1775319562427f95cca`.

Verified actual TIGER artifact:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43651609278/artifacts/14136592595 .

Actual HIFLD-vs-TIGER **equal-area mask overlap** independent of weather is implemented in `src/c2_hifld_vs_county_spatial_overlap.py` and GitHub run https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43652536420 .

The real ERA5 **matched-hour air temperature** comparison is in `src/c2_census_vs_hifld_era5.py` and source-triggered GitHub run https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43652340209 . As of the latest check both downstream jobs are **queued** with no numeric geometric-overlap or actual temperature comparison result verified yet. Do not claim a magnitude or direction of spatial exposure bias.

All county proxies stay `geometry_approved=False` and `model_training_eligible=False`. Stable county membership and valid Census geometry do not certify a historical electricity BA operating area.
