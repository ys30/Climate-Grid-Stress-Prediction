# E1 live source audit — public ERA5 verified, four-BA geographies NOT verified

Recorded November 12, 2026.

## GitHub Actions audit and distinction between actual observations and unit fixtures

| Stage | Workflow run | Verified result |
|---|---|---|
| Real ARCO ERA5 source cell | https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317179422 | **Success**. One actual 2m temperature: 284.3685607910156 K (11.2185607910156 °C) at 2023-07-01 12:00 UTC request, around 35°N, 112°W. This is **not BA-area weather** |
| ERA5 0.25° overlap weight unit fixtures | https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317318235 | **Success** on synthetic polygons only |
| Grid-area hourly aggregation unit fixtures | https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43317715313 | **Success** on synthetic gridded Kelvin arrays only |
| HIFLD Control_Areas_OR candidate discovery | https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43323359377 | **Success** after installing scientific test dependencies; 16 source polygons received, but only **BPAT** and **CISO** candidate name matches |
| Full repository test suite | latest successful run after E1 dependency fix | **Success** after installing numpy, xarray, shapely, pyproj before test discovery |

## Material geographic blocker

The queried ArcGIS service is `Control_Areas_OR`; it returned 16 geometries. BA-name candidates found:
- **BPAT**: BONNEVILLE POWER ADMINISTRATION, source ID 1738, source field YEAR=2020, geometry MultiPolygon.
- **CISO**: CALIFORNIA INDEPENDENT SYSTEM OPERATOR, source ID 2775, source field YEAR=2020, geometry MultiPolygon.
- **AZPS and SRP not present in this queried subset**.

The service itself cannot populate the full four-BA exposure weights. Nor do its reported names and year alone authorize the BPAT/CISO features as historically stable BA territory. A proper national **Control Areas** archival source is more appropriate: 
https://www.datalumos.org/datalumos/project/239072/version/V1/view
(public HIFLD OPEN Control Areas GeoJSON archival snapshot, circa 2025, 2022–2025 estimated coverage). This is a *candidate source*, not yet ingested or checked for four BA IDs. A separate official/source geodata reviewer must still verify code mapping, area completeness, overlaps, geometries, and temporal representativeness.

**DO NOT** quietly replace missing AZPS/SRP BA polygons with Arizona state or Salt River Project headquarters buffers, or treat the two candidate polygons as automatically approved.

## Scientific conditions for first empirical grid exposure

1. Verify source delivery and content SHA256; save version/license and code-to-BA name crosswalk audit, plus explicit source-vintage limits.
2. Prove all four BA polygons are present and geometrically valid, without merging noncontiguous boundaries incorrectly.
3. Compute intersected 0.25° ERA5 grid-cell weights with equal-area EPSG:5070; verify each BA normalized weights sum to 1 and no zero-overlap.
4. Stream a bounded, true gridded ERA5 2m temperature region/time subset (do not fetch multi-petabyte Zarr; this store is chunked in single-hour *global* grids, potentially expensive in sustained egress). 
5. Ensure source ERA5 validity time is aligned to EIA-930 UTC interval-start labels by an **explicit** weather-time convention; preserve alternate ±1-hour lag checks for interpretation. Then perform the existing strict complete-case join.
6. Only after a fully observed source panel and QA gates, fit calendar baselines / GAM / XGBoost; keep 2024–2025 test sealed.

This stage does not yet estimate weather sensitivity, historical anthropogenic climate attribution, forecast skill, or future power-grid unserved energy.
