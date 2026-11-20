# E2 ERA5 source options and real public-source evidence — 2026-11-19

## Verified empirical fact: public ARCO ERA5 is readable without CDS credentials

Prior independent source probe succeeded:

- GitHub Actions: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317179422
- Artifact ID: `13988243525`, `c2-e1-real-public-era5-source-probe`
- Sample source: `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`
- UTC sample: 2023-07-01T12:00:00Z, 35N 112W
- Verified sample: 284.3685607910156 K = 11.2185607910156 °C
- Source grid coordinate: 35N, longitude 248°E
- **This is one actual real ERA5 grid sample, NOT a validated BA geographic exposure.**

The ARCO URL is the Google-reformatted publicly hosted ERA5 Zarr source,
not a Copernicus CDS NetCDF download. Its cloud storage source is not
independently immutable-SHA-pinned as a whole. Therefore logs and derived
sample manifest MUST report the store URI and exact requested UTC values,
and the resulting *local output* SHA-256, without implying a whole-store
cryptographic original-source proof.

## New 24-hour observational experiment

- Script: `src/c2_era5_public_daily_probe.py`.
- Offline contracts: `tests/test_c2_era5_public_daily_probe.py`.
- Workflow: `.github/workflows/c2-era5-public-daily-pilot.yml`.
- Registered date/location: **2024-02-01 00:00–23:00 UTC** at grid point
  near **38.5N, 121.5W**.
- Manifest declares `public_ARCO_ERA5_Zarr_one_gridcell`, checks 24 unique
  valid UTC hours, Kelvin input, Celsius output and output CSV SHA-256.
- Explicitly sets `ba_exposure_qualified=false` and `joined_to_eia=false`.
- Current workflow start was issued by GitHub push as run
  https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44678645391
  **(queued when documented)**. No empirical 24-hour values are asserted
  until that run and artifact have independently passed.

## Relationship to official CDS source path

The CDS `cdsapi` monthly NetCDF path remains valid, but depends on CDS
account credentials and licence acceptance. The public ARCO Zarr path can
provide a **credential-free** hourly ERA5 grid source for source-level
experiments. Neither pathway alone establishes geographic suitability
for CAISO / CISO balancing area. Annual EIA 2020–25 source data alone
also cannot establish EIA × ERA5 joint coverage.

## CI engineering repair

The broad `phase1-ci.yml` workflow was repeatedly failing for two
unrelated test-harness problems: the mocked EIA local-runner test
incorrectly searched the subprocess argument list for an exact module
name, and the global test runner lacked an available NetCDF backend.
Changes to `tests/test_c2_eia_local_pilot.py` and
`.github/workflows/phase1-ci.yml` correct these, pending confirmation
by the **new** workflow runs, not older failures.

## Next genuine research gates

1. Confirm 24-hour ARCO pilot artifacts and hourly provenance.
2. Freeze and document real BA spatial polygons / ERA5 grid-cell area
   weights, not load-weighted fictitious county observations.
3. Expand to one calendar month, preserving valid-time clock and continuous
   hourly coverage; then six CISO years.
4. Only after provenance-gated BA-hour aggregation join against already
   SHA-verified EIA CISO demand and run temporal leakage-safe model
   comparison.

Canonical EIA source gate remains 23/24, with AZPS 2023's two negative
original EIA observations reserved for separately labeled noncanonical
sensitivity analysis. C-1 frozen evidence remains untouched.
