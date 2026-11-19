# E2 ERA5 official source pilot: time semantics and source-eligibility gates

Status on 2026-11-19: **request specification, source extractor and offline tests submitted; no official ERA5 download has been verified**.

## Why ERA5 2m temperature must not receive EIA's one-hour shift

- EIA-930 D uses UTC hour-ending labels; its original source hour is shifted back one hour to match an hourly interval-start.
- ERA5 2m air temperature is an **instantaneous analysis value at its UTC validity time**; do not subtract one hour. For weather effects on demand, contemporaneous instantaneous temperature must be aligned with the corresponding hourly demand interval as a declared modeling choice, with alternative temperature leads/lags checked separately.
- Reference: https://confluence.ecmwf.int/pages/viewpage.action?pageId=111150947

## Official dataset, constraints and phased acquisition

- Official dataset: Copernicus CDS `reanalysis-era5-single-levels` hourly `2m_temperature` in kelvin.
- Official retrieval API instructions: https://cds.climate.copernicus.eu/en/how-to-api
- A CDS account with active API credentials and the dataset licence accepted is a prerequisite for actual retrieval; the EIA_API_KEY cannot access CDS. **No CDS key is currently confirmed in the C-2 GitHub Secrets.**
- Preliminary request and source: `scripts/c2_era5_official_pilot_request.py` (2024-02 illustration; every hour, leap February).
- NetCDF source extraction: `scripts/c2_era5_single_gridcell_extract.py`; yields source SHA-256, derived CSV SHA, selected grid point coordinates, original temporal definition and 696 valid hours in a complete February 2024 fixture.
- Offline test: `tests/test_c2_era5_official_pilot.py` — fixture data **are synthetic**; no empirical meteorological result implied.

## Critical spatial guard

The selected approximately 38.5N, 121.5W grid point is only a Sacramento-area example, **not** a validated CISO-wide weather exposure. The output manifest says `ERA5_SINGLE_GRIDCELL_DEMONSTRATOR_NOT_BA_PROXY` and deliberately fails the existing `ERA5_BA_geographic_proxy` source requirement. This prevents an illustrative point from being silently promoted into regional climate-impact claims.

Before moving to 2020–2025 six-year joint EIA–ERA5 modeling:

1. Authenticate official CDS acquisition and preserve original netCDF source plus immutable SHA manifest.
2. Specify and justify geographic weighting: actual CISO BA extent/grid-cell overlap or a transparent set of documented population/load proxy grid weights; without independent load geolocation, use an **unweighted grid-cell spatial mean** only, with explicit geospatial limitation.
3. Produce signed BA-hour weather proxy for the full 2020–2025 period and audit ERA5 hourly UTC validity time and Kelvin→Celsius conversion.
4. Join only SHA-verified official sources and pass EIA × ERA5 annual **joint** coverage gate.
5. Maintain train 2020–22, validation 2023 and test 2024–25 with leakage-safe model features and appropriately aligned forecast issue times.

## AZPS 2023 source anomaly is separate

The authenticated AZPS 2023 data show exactly two negative published EIA values. Canonical EIA source audit remains **23/24**; the verified sensitivity dataset is a *noncanonical* derived artifact excluding exactly those two observations. This does not change the source gate or establish ERA5 weather joint eligibility.

C-1 repository/results are frozen and untouched.
