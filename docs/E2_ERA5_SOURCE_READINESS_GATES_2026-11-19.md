# ERA5 E2 source readiness: implementation and evidence gates (2026-11-19)

## What is implemented and what is NOT yet empirically proven

Four code/test changes were made to the existing official Copernicus ERA5 pilot:

1. `scripts/c2_era5_single_gridcell_extract.py` requires original source
   `.manifest.json`, correct ERA5 single-levels dataset identity, selected
   year/month, and a byte-matching NetCDF SHA-256 **before** xarray parsing.
   Synthetic fixture provenance is explicitly distinct from official CDS
   provenance. Derived CSV never claims validated CISO BA coverage.
2. `tests/test_c2_era5_official_pilot.py` asserts failed provenance on
   tampered NetCDF and on a missing source manifest; the offline fixture is
   explicitly labeled `SYNTHETIC_TEST_NETCDF_ONLY`, not official ERA5.
3. `scripts/c2_era5_official_pilot_request.py` requests exactly the
   calendar-valid days for each month (2024 February 29 days, 2023 February
   28 days), and `tests/test_c2_era5_official_pilot.py` checks this.
4. `.github/workflows/c2-era5-cds-official-pilot.yml` remains a manual,
   authenticated workflow: no CDS key is committed, printed, or substituted
   with EIA credentials. The source NetCDF, source manifest, derived UTC
   gridpoint CSV, and converted manifest are uploaded as Actions artifacts.

**Not yet evidenced:** actual successful CDS download, actual ERA5 hourly
NetCDF with SHA-verified manifest, EIA × ERA5 joint coverage, six-year
CISO BA weather proxy, fitted weather model, or climate-change attribution.

## Correct temporal semantics and evaluation

- EIA-930 source demand labels are UTC hour-ending; for hour interval start
  the source timestamp is shifted -1 hour with source label retained.
- ERA5 instantaneous t2m timestamps represent UTC validity time; they are
  **not shifted** by EIA's clock conversion.
- The pilot's near-Sacramento point is only an illustrative weather sample,
  not a CISO-wide geographic or load-weighted exposure measure.
- Official ECMWF ERA5 docs:
  https://confluence.ecmwf.int/pages/viewpage.action?pageId=235634513
- Official CDS API setup:
  https://cds.climate.copernicus.eu/en/how-to-api

## Actual next evidence requirements

1. User sets secret `CDSAPI_KEY` after accepting ERA5 CDS dataset terms,
   then manually runs `c2-era5-cds-official-pilot.yml` using 2024-02.
2. Validate job/test success and download the real Actions artifact. Recompute
   original NetCDF and grid CSV SHA-256 independently; confirm Feb 2024 has
   exactly 696 unique UTC valid hours.
3. Obtain defensible CISO BA geometry and spatial averaging specification.
   No county sales allocation is invented; if BA grid-cell coverage cannot
   be proved, geographic representativeness must remain an explicit limitation.
4. Only then create authenticated `ERA5_BA_geographic_proxy` hourly inputs
   for all years; use the existing provenance join and annual joint coverage
   gate before any predictive model claims.

## Existing EIA research foundation

- Official source quality gate: 23/24 independent BA-year cohorts.
- AZPS 2023 fails strict canonical gate due to two original negative values.
  A separate, SHA-verified, noncanonical sensitivity data artifact exists,
  retaining 8758 valid hours, with original source kept immutable.
- C-1 frozen study and evidence are not modified.
