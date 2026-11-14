# C2 E1 — 2026-11-14 source-verified historical geography and 70 anomaly candidates

## Summary of actual work performed

The existing historical E1 real hourly ERA5 and EIA-930 source archive contains **210,432 BA-hour records**, 210,172 nonmissing EIA-930 original demand/weather pairs, 260 source demand gaps and **70 source candidate anomalies**. They remain strictly source-quality evidence and NOT an approved analytic model panel.

### A. All 70 original demand anomaly candidates triaged numerically (actual archived data)

Complete CI SUCCESS: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43646854297 . Archive artifact and row-by-row CSV: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43646854297/artifacts/14134356821 .

The isolated source anomaly screen flagged a center hour if it exceeded 2× or fell below 0.5× the arithmetic mean of adjacent original demand hours. An independent *triage*, not correction, then compared each flagged hour with a median of up to 3 preceding and 3 following **unflagged, observed** original hours from the same BA:

| Review triage class | Candidate records |
|---|---:|
| ≥3× neighbor median (large positive) | 20 |
| ≤1/3× neighbor median (large negative) | 1 |
| Moderately outside neighbor median (≥1.5× or ≤2/3×) | 8 |
| No large median discontinuity across expanded window | 41 |
| **Total** | **70** |

A lack of large median discontinuity in an originally flagged record does not imply original flag erroneous: the original immediate-neighbor test can flag the surrounding hours of a huge isolated spike. The 41 may include such spillovers. None of these candidate labels proves the source measurement was erroneous; independent source revision/history must precede exclusion or correction.

Example large spikes from actual source: AZPS at 2020-01-22T15:00Z reported 101,412 MW (≈35.415× selected neighbor median); SRP at 2023-07-22T00:00Z reported 40,613 MW (≈5.418× selected neighbor median). The source remains unchanged; no interpolation or model fit.

### B. Independent 2020–2025 historical BA-to-county source verified

First source inventory CI SUCCESS: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43647065832 . Verified actual public PUDL/EIA-861 county source 126,489 records spanning 2015–2025.

Annual EIA-861 BA-code/BA-ID / county crosswalk CI SUCCESS: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43647297586 . Download annual BA/code IDs, yearly exact county FIPS membership, county pair overlaps, and annual county Jaccard audits: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43647297586/artifacts/14134338768 .

Actual EIA-861 annual sources read: 2,559 BA identity rows (`core_eia861__yearly_balancing_authority`) plus 126,489 BA-county membership records (`out_eia861__yearly_balancing_authority_service_territory`). The subset of **four BAs over six years** contains exactly **24/24 code-ID matches, 24/24 county sets, and 1,110 annual BA–county membership rows**.

| EIA-930 BA code | PUDL/EIA-861 BA ID (all years) | EIA-861 county memberships per year |
|---|---:|---:|
| AZPS | 803 | 15 |
| BPAT | 1738 | 109 |
| CISO | 2775 | 58 |
| SRP | 16572 | 3 |

**Independent source observation:** all 20 consecutive-year comparisons (four BAs × five transitions, 2020→2025) had zero counties added or removed, with county-membership Jaccard = 1.0. This is stable *county membership* at the available geographic granularity, **not proof that physical utility service footprints or operational BA jurisdiction stayed unchanged**.

AZPS and SRP overlap in **exactly three county FIPS codes** in every year: 3/3 SRP counties, 3/15 AZPS counties. County-level overlap is **not area overlap** and is not proof that reported EIA hourly demand is double-counted. HIFLD 2018 `make_valid` polygons separately showed 25,441.575 km² intersection, 96.66% of source SRP candidate area. These observations qualitatively reinforce the need to treat BA masks as non-exclusive and to evaluate alternative spatial exposure estimands.

Two reproducible source files (public anonymous S3 parquet):
- `s3://pudl.catalyst.coop/nightly/core_eia861__yearly_balancing_authority.parquet`
- `s3://pudl.catalyst.coop/nightly/out_eia861__yearly_balancing_authority_service_territory.parquet`

**Important reproducibility caveat:** PUDL `nightly` can change; the GitHub artifact preserves the output crosswalk but raw Parquet files have NOT been snapshotted/pinned by release in this workflow. Prior to publication freeze a stable PUDL release and source checksums; validate all county membership IDs against the pinned release. The HIFLD polygons remain preserved in earlier source-artifact provenance.

### C. Methodological authority and geographic admissibility

- EPA eGRID2022 Technical Guide, §3.4.1 (printed page 23): https://www.epa.gov/system/files/documents/2024-01/egrid2022_technical_guide.pdf . EPA states BAs are not strictly geographically based and therefore does not provide eGRID2022 BA shapefiles. A county proxy, service-area polygon, HIFLD Control Area polygon and actual hourly BA load are **not interchangeable**.
- Official EIA-930 reporting roles and codes: https://www.eia.gov/electricity/930-content/about.html .
- EIA-861 county-territory table metadata and analytical derivation: https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html and https://docs.catalyst.coop/pudl/en/latest/autoapi/pudl/analysis/service_territory/index.html .
- Archived HIFLD control areas: https://www.datalumos.org/datalumos/project/239072/version/V1/view .
- SRP retail service area metadata is not BA operational support; its publication restrictions mean raw SRP GIS layer must **not** be redistributed without permission: https://services2.arcgis.com/ICaY8VX3lsUsMBRl/arcgis/rest/services/SRP_PSA/FeatureServer/3/metadata?f=html&format=default .

### D. Gate decision and next executable work

Current E1 source archive and county IDs are both real and complete at their described data granularities, but `historical_BA_geography_approved=False` and `model_training_permitted=False` remain enforced. Source count/Jaccard stability alone is insufficient to validate four model exposure masks, especially given CISO original polygon topology sensitivity (~7.08% diagnostic) and AZPS/SRP near-overlap.

The next highest-value executable result is to use **pinned Census county geometries** to construct separate county-derived ERA5 area-weight masks for 2020–2025, compare weighted actual ERA5 exposures against the old HIFLD candidate masks on a subset of time points, and evaluate actual geographic sensitivity under alternative masks. Treat county proxy as *independent but approximate*—do not automatically admit GAM/XGBoost. Analyze original 70 suspect values relative to EIA official revision or balance data before calling them confirmed errors. Keep chronological 2024–2025 test untouched until training admission.

C-1 remains frozen; Project C-2 only. No climate attribution or SSP/PyPSA future grid stress results are claimed.
