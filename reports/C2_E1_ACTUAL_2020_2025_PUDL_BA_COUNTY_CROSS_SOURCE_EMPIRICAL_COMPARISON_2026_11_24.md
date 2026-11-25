# C-2 E1 — ACTUAL 2020–2025 PUDL annual BA-county cross-source comparison (2026-11-24)

## New verified original-artifact result

Recovered and reopened the actual historic GitHub Actions archive **14134338768** (PUDL historical **nightly** source as collected) and separately downloaded original archive **14393473675** (PUDL fixed v2026.10 observed **2020–2023** utility–BA–state county support records). Independently extracted actual CSV bytes and SHA-256, did not infer values from documentation. Full source ZIPs, deterministic Python reproduction script, 16-cohort and 24-cohort CSVs, original manifests and verification instructions are bundled in **`C2_PUDL_2020_2025_Real_BA_County_CrossSource_Audit_2026_11_24.zip`**, SHA-256 `7bd0e7085e12e82087679b66c526cbb7a27115a70a154aa8a9dee9b275897a2e`.

| BA | 2020–2025 historic nightly county count in each year | 2020–2023 *set-union* agreement with fixed PUDL utility-source county records |
|---|---:|---|
| AZPS | 15 | 4/4 BA-years exactly equal |
| BPAT | 109 | 4/4 exactly equal |
| CISO | 58 | 4/4 exactly equal |
| SRP | 3 | 4/4 exactly equal |

**Computed from actual files:** 24 annual BA-year source sets, exactly **1,110** unique BA/year/county source records; **20 of 20** within-BA annual county-set transitions have Jaccard 1.0 with no reported added/removed county. From fixed v2026.10 source utility records, **933** real utility–BA–state–year association rows were unioned into **16** 2020–23 BA/year source sets. **16/16** fixed-source unions are identical to corresponding nightly annual county source sets (all source-set Jaccard 1.0).

### Critical non-independence and coverage limits

Both source constructions derive from **EIA-861** and are not independent observations of historical BA system operations. The nightly source is **not an immutable release version**; it is only byte-frozen as collected in historic GitHub artifact 14134338768. The fixed release utility source has service-county gaps and overlaps; agreement between **unions** can conceal large differences in company coverage, actual delivered MWh and hourly demand. E.g. **CISO** yearly set is all **58 California counties** while fixed source has **51,52,51,53** utility–BA–state associations **lacking county support** in 2020–23 out of **89,89,89,94** total. AZPS counts with no counties are 14,11,11,12 out of 26,23,23,24; SRP 7,6,6,6 out of 9,8,8,8. These figures are reporting **associations**, *not* customers or MWh.

Hence "county-set unchanged" proves **no change in the recorded coarse support unions** in this source sample, NOT that the actual operator-certified BA footprint was unchanged 2020–25. The union's spatial coverage is too coarse to supply load-weighted exposure, true BA physical boundaries, or credible historical boundary changes. No 2024–25 fixed-release utility-source comparison was performed, and no new authentic PUDL original GeoParquet was acquired.

## Reproducibility and scientific decision

Input GitHub artifact IDs: 14134338768 and 14393473675. Delivered ZIP includes their exact source ZIPs, integrity-manifest JSON, 24-year annual summary CSV, 16-year cross-source comparison CSV, `c2_real_pudl_2020_2025_geo_comparison.py`, and README. The package was reopened and every inner file was individually SHA-checked. This actual-source script checks exact BA/year cardinality, unique BA/year/county rows, fixed-source FIPS cardinalities and produces strict not-approved flags.

Scientific disposition: **PUDL annual county-support is now empirically cross-checked as a repeatable, overbroad 2020–25 proxy**, but **`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `GEO_LOAD_RELEVANCE=BLOCKED`, `model_training_permitted=false`**. Previous EIA-930 demand vintage inconsistencies, AZPS2023 canonical QA failure and explored 2025 holdout remain open. No load forecast training, climate-attribution, SSP projection, or PyPSA simulation claims. **C-1 frozen and untouched**.

**Next empirical route:** seek independent date-qualified operating-area evidence (CEC 1305 for CISO where available, other operators or balancing-area metadata for AZPS/BPAT/SRP) and independent within-BA load-weighted geographic evidence, rather than treat unchanged EIA861 county unions as validated time-varying geography.
