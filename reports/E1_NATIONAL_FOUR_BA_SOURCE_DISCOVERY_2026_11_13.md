# E1 national four-BA control-area discovery and geometry gate (2026-11-13)

## Verified result — national ArcGIS attribute inventory
Successful CI: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43527911436

National Control_Areas ArcGIS layer:
https://services5.arcgis.com/HDRa0B57OVrv2E1q/ArcGIS/rest/services/Control_Areas/FeatureServer/0

The script `src/c2_national_control_area_discovery.py` independently retrieved and SHA256-audited all **71** distinct OID attribute records, matching all four predeclared EIA-930 BAs by original `NAME` field:

| BA | OID field OBJECTID_1 | Exact original NAME |
|---|---:|---|
| AZPS | 23 | ARIZONA PUBLIC SERVICE COMPANY |
| BPAT | 4 | BONNEVILLE POWER ADMINISTRATION |
| CISO | 11 | CALIFORNIA INDEPENDENT SYSTEM OPERATOR |
| SRP | 36 | SALT RIVER PROJECT |

This resolves the geographic **name-coverage** gap caused by querying the Oregon-focused `Control_Areas_OR` service.

## Extraction stage
New pipeline:
- `src/c2_national_polygon_extract.py`
- `tests/test_national_polygon_extract.py`
- `.github/workflows/e1-national-polygon-extract.yml`

It requests **four exact OIDs** in layer-supported GeoJSON format, checks each name/OID crosswalk again, confirms geometries are nonempty and valid, reports equal-area polygon sizes, and publishes source SHA256 plus original extracted GeoJSON. The downloaded geography is explicitly marked **UNAPPROVED**. CI run: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43528134677. At documentation time it is queued, so no four-polygon result is claimed.

## Important limits
These are Control Areas, not proven time-varying operational boundaries for each BA in 2020–2025. The public service's data-last-edited date is 2021-02-25 per the ArcGIS layer's service directory; this alone does not establish the original `YEAR`, `SOURCEDATE` and `VAL_DATE` representativeness for the study years. Those per-feature fields are captured for inspection, along with source vintage.

Even if all four polygons validate topologically, review is still required for mismatched reporting versus service territories, completeness of polygons, overlap/multi-polygons and bias in population- or load-weighted exposures. The current area-weighted ERA5 model cannot be declared scientifically approved by the network query alone.

## Current status
E0 EIA-930 source time-boundary and missingness QA is independently CI verified. A single real ARCO ERA5 grid sample was fetched successfully in E1. Area-aggregation unit tests passed on synthetic fixtures. **There is still no verified multi-BA gridded ERA5 × hourly-demand panel, historical weather-response model, or SSP grid-stress forecast.**

Next actual data gate: inspect geometry extraction CI, then compute provisional (NOT modeling-admitted) area-overlap grid-weight evidence, verify exact source geometry vintage and conduct uncertainty/sensitivity analysis before admitting as actual BA exposure.
