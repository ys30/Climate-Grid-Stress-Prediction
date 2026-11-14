# E1 real four-BA national polygon topology gate — 2026-11-13

## Independently observed source findings
- Source: national ArcGIS Control_Areas FeatureServer, 71 control area attribute records.
- Name/OID matches: AZPS 23, BPAT 4, CISO 11, SRP 36.
- First extraction CI failed because it stopped on topology invalidity **before publishing diagnostic artifacts**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43528134677.
- Revised diagnostic extraction CI succeeded and preserved the raw, unchanged GeoJSON plus source hashes: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43540859017.

## Per-feature original geometries
| BA | Type | Shapely validity | Reason | Source YEAR |
|---|---|---|---|---|
| BPAT | MultiPolygon | invalid | Nested shells at [-122.75831,48.99429] | 2018 |
| CISO | MultiPolygon | invalid | Ring self-intersection at [-116.391101837158,33.6416206359863] | 2018 |
| AZPS | MultiPolygon | invalid | Nested shells at [-111.7251,33.9999500000001] | 2018 |
| SRP | Polygon | valid | Valid geometry | 2018 |

All four source records show SOURCEDATE 1560988800000 and VAL_DATE 1589500800000 (epoch milliseconds); name and YEAR fields therefore do **not** establish 2020–2025 boundary currency.

## Scientific interpretation

Three of four national source polygons are topologically invalid in Shapely as supplied. Direct intersection-based ERA5 BA area weights therefore remain **BLOCKED**. The SRP candidate polygon alone being valid does not approve it for historical BA-area demand exposure.

The topology diagnostic workflow `e1-topology-sensitivity.yml`, run https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43540956239, compares original projected raw area against Shapely `make_valid` derived **polygonal** geometry, reports whether repaired outputs include non-polygon fragments, and stores a separate explicitly **UNAPPROVED** derived GeoJSON. The source original remains unchanged. Repair is a methodology sensitivity check and is **not** source validation or authority to fit a weather-response model.

After repair candidate audit, independently review geographic coverage, legal licensing, period currency, geometry component losses and 0.25° grid weight sensitivity; do not automatically toggle the `code_crosswalk_reviewed` admission flag. The E1 empirically weighted 2020–2025 ERA5 × EIA-930 panel remains not yet produced; neither forecast skill nor future SSP grid stress has been estimated.
