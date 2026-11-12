# C-2 E1: audited gridded ERA5 → BA exposure acquisition protocol (2026-11-12)

## Status: engineering implemented; measured full-region ERA5 exposure not yet certified

- Public ARCO-ERA5 single-cell source test: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317179422
- HIFLD geometry candidate discovery: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317462968
- Strict geometry-to-ERA5 grid-weight tests: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317318235
- Strict area-weighted 2 m temperature aggregation tests: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317715313

**These are independently queued GitHub jobs, not evidence of successful ERA5 data acquisition unless their logs, result and artifacts confirm success.** In particular, unit tests on synthetic polygons are never observed BA weather measurements.

## Public weather data source

1. Google Research ARCO ERA5: `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`, 0.25-degree latitude–longitude, hourly. Official source: https://github.com/google-research/arco-era5. Source 2 m temperature uses Kelvin; compare its time, grid and version attributes in the source probe and source manifest. A single chosen grid cell for API reachability is explicitly **not** the BA weather exposure.
2. Official ECMWF/Copernicus CDS: dataset `reanalysis-era5-single-levels`; use versioned per-month NetCDF for the weight-aggregation path. https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels. The owner must authorize CDS access and accept terms; no credentials are present or silently invented here. Alternative CDS ARCO subset access: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-timeseries?tab=analysis_ready_data.
3. Do not confuse ERA5 **analysis validity time** with one-hour accumulation windows for precipitation/radiation. Air temperature is an instantaneous 2 m parameter; align its timestamp to EIA-930 start-hour by an explicitly documented observational convention and sensitivity check. A temporal shift must never be guessed from temperature values.

## BA geography and scientific exposure estimand

- HIFLD Control Areas (public ArcGIS service): https://services.arcgis.com/uUvqNMGPm7axC2dD/arcgis/rest/services/Control_Areas_OR/FeatureServer/0
- The apparent 2025 version does **not** establish accurate 2020–2025 BA territories, geography stationary over time, or load spatial weights; codes must be reviewed against EIA-930 names and source provenance. It is a **candidate geometry layer** only.
- `src/c2_hifld_geometry_discovery.py` downloads feature metadata and produces suggested BA name matches with `no_auto_mapping=True`; it does not assert approved polygons.
- `src/c2_ba_era5_weights.py` accepts an externally reviewed four-BA GeoJSON `FeatureCollection` where each feature has `properties.ba` equal to AZPS/BPAT/CISO/SRP; plus a provenance JSON containing source URL/vintage/license, exact GeoJSON SHA-256 and signed-off BA-code crosswalk boolean. The script checks values and geometry; no default polygons are fabricated.
- ERA5 cell center coordinates are on the 0.25-degree grid. Compute cell–polygon overlap in EPSG:5070 equal-area projection, and normalize positive weights to sum to 1 within each BA. This is **area-weighted air temperature**, not load-weighted demand exposure. Sensitivity work should compare these with independently identified, population/load-weighted weights where available.
- Geometry source must be stable in a data snapshot and licensed for analysis; **area boundaries are not guaranteed to coincide with power generation/load balancing regions**. Uncertain geography should be propagated in the manuscript, not hidden.

## Hourly aggregation and strict joins

`src/c2_era5_area_aggregate.py` accepts an actual gridded ERA5 NetCDF subset and frozen weight table. It requires:
- ERA5 Kelvin units and exact compatible grid coordinates, no silently nearest fallback or interpolation.
- Hourly UTC observations, no duplicate timestamps, and complete weighted grid coverage for each reported BA-hour. Missing grid values go to an exclusion/audit file.
- Emits `hourly_ba_era5_exposure.csv` (`ba`, `timestamp_utc_start`, `temperature_2m_c`, `exposure_method`, `source_dataset`) with source and weight hashes, accepted by `src/c2_weather_join.py`.
- Existing EIA-930 boundary-reconciled, observed demand hours must be joined via UTC hour keys, *excluding* original blank periods and candidate source anomalies from the primary fit. Raw values remain accessible for quality review and alternate robust sensitivity tests.

## Ready-to-run commands after source authorization

```bash
python -m src.c2_ba_era5_weights --geometry audited_ba_boundaries.geojson \
  --metadata approved_geometry_provenance.json --out outputs/e1_weights

python -m src.c2_era5_area_aggregate --era5 era5_hourly_subset.nc \
  --weights outputs/e1_weights/ba_era5_grid_weights.csv \
  --weights-manifest outputs/e1_weights/weights_manifest.json \
  --out outputs/e1_hourly

python -m src.c2_weather_join --demand audited_raw_eia930_quarantine.csv \
  --weather outputs/e1_hourly/hourly_ba_era5_exposure.csv \
  --out outputs/e1_joined
```

These are **conditional**, not commands already run successfully on observed BA polygons. Until source geometry and actual ERA5 hourly grid coverage are validated, no combined weather–demand panel, calibrated climate effect, prediction or grid stress outcome is claimed.

## Reference for historical source eligibility

Six-year EIA-930 source data + January boundary recovery and contiguous source gaps have already been independently executed and documented in `reports/E0_2023_2024_BOUNDARY_RECONCILIATION_AND_RAW_OUTLIERS.md` and `reports/E0_EPISODE_QA_TO_E1_ERA5_JOIN_GATE.md`.
