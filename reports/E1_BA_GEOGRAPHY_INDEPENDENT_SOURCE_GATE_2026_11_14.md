# C2 E1 — Independent balancing-authority geographic admissibility review (source verification)

Research gate date: 2026-11-14. **Verdict: NOT APPROVED** for calendar/GAM/XGBoost exposure modeling. This report changes no C-1 materials and does not alter the original 210,432-row E1 source archive.

## 1. Independent authoritative evidence and why the 2018 HIFLD polygons are not enough

**US EPA eGRID2022 Technical Guide**, January 2024, §3.4.1 (printed page 23; PDF page index 33): https://www.epa.gov/system/files/documents/2024-01/egrid2022_technical_guide.pdf

EPA directly explains that balancing authorities are **not strictly geographically based**, and that eGRID2022 does not provide BA shapefiles for this reason. Therefore an area-polygons-only weather estimand is a *modeling assumption* needing sensitivity checks, not an intrinsic or official partition of the electricity load.

**US EIA Form EIA-930**, official description: https://www.eia.gov/electricity/930-content/about.html . Demand and interchange are **reported by balancing authorities** performing grid operating roles. EIA identifies BA by formal NERC-related codes and notes BA code/name changes. An AZPS/SRP overlap seen in polygons cannot automatically be interpreted as duplicate reported demand, nor can a geometrically repaired polygon be presumed the same reporting support as hourly demand.

**HIFLD OPEN Control Areas**, preserved 2025 geo-source archival copy: https://www.datalumos.org/datalumos/project/239072/version/V1/view . The source describes actual control-area features, and its archived files include a feature-data GeoJSON and metadata. This can provide an independent snapshot comparison but does NOT establish correct year-by-year EIA demand exposure. The present source-origin four BA candidate polygons are tagged YEAR=2018.

**EIA-861 historical geographic proxy, via PUDL**: https://docs.catalyst.coop/pudl/en/v2026.6.0/data_dictionaries/pudl_db.html#out-eia861-yearly-balancing-authority-service-territory ; and the documented PUDL county-based historical territory derivation: https://docs.catalyst.coop/pudl/en/latest/autoapi/pudl/analysis/service_territory/index.html . This table contains annual BA ID / county FIPS relationships derived from EIA-861. It offers a *temporally indexed county-level proxy*, not a parcel-level electrically exclusive BA polygon. Its year availability, BA ID crosswalk, county overlap and 2025 coverage must be **empirically checked** prior to using it.

**EIA-861 service-territory files**: https://www.eia.gov/electricity/data/eia861/ . These report counties and states where utilities distribute electricity, not meter-accurate BA load distributions. A utility-to-BA mapping and county geometry can produce a reproducible alternative sensitivity definition, not magically reveal a true operating area.

**SRP Power Service Area metadata**: https://services2.arcgis.com/ICaY8VX3lsUsMBRl/arcgis/rest/services/SRP_PSA/FeatureServer/3/metadata?f=html&format=default . This is *SRP's retail service area* defined by historical agreements, not necessarily SRP's EIA-930 reporting BA support. SRP's stated use restrictions include **no redistribution outside SRP without permission**; do NOT copy the map or republish its raw geometry. Use metadata for source-interpretation assessment only unless permission is obtained.

## 2. Four-BA 2018 source geometry audit already computed

| EIA BA code | HIFLD feature object ID | Raw geometry topology | Provisional `make_valid` area-weight cells | Historical geographic authorization |
|---|---:|---|---:|---|
| AZPS | 23 | invalid nested shells | 265 | No |
| BPAT | 4 | invalid nested shells | 1,557 | No |
| CISO | 11 | invalid self-intersection | 662 | No |
| SRP | 36 | valid source polygon | 55 | No |

CISO's `make_valid` candidate differs by ~7.08% from raw invalid-geometry projected-area arithmetic. This is a topology sensitivity diagnostic, **not** measured service-boundary change or spatial measurement uncertainty.

The 2018-source-derived AZPS and SRP candidate masks overlap in 25,441.575 km²: ~96.66% of SRP candidate area and ~19.90% of AZPS candidate area. There is no evidence that the 2018-source polygons form disjoint geographical supports of 2020–2025 BA load. To claim they are disjoint, or to use them as validated electric-load service-area estimates, would be indefensible.

## 3. Proposed independent geographic estimands (NOT RESULTS)

- **A: Historical control-area approximate mask.** The current HIFLD candidate (already available, 2018 vintage), documented as unapproved. Reweight actual ERA5 2m by 0.25° cell intersection fraction; this is the existing *exploratory* E1 source panel, not training data.
- **B: EIA-861 / PUDL annual county-membership BA proxy.** Crosswalk EIA-930 BA code to annual EIA-861 BA ID, then use *census county polygons* and map county membership by year. Compute area-weighted and population-weighted exposures as separable candidate estimands. Must check completeness and nonunique county membership. Do not imply each county belongs to exactly one BA; no exclusive partition assumption.
- **C: Electricity load/customer-weighted proxy.** If independently released, year-specific utility customer counts, sector/end-use or meter locations and mappings could weight weather by actual served load. This is a preferred exposure concept for demand attribution but not yet observed or approved.
- **D: Robustness.** Demand models should be run under at least two defensible exposure definitions *after* independent authorization. Report changes in BA temperature exposure and model coefficients/test losses, especially CISO and AZPS/SRP. The 2024–2025 prediction test is held out.

## 4. Geographic acceptance gates (all currently CLOSED)

1. Confirm code mapping AZPS/BPAT/CISO/SRP to year-specific EIA reporting identities with documented source references, including any changes in EIA-930 respondent scope.
2. Choose or construct an independently derived 2020–2025 BA geography proxy with known source license, valid geometry, vintage, coordinate system and uncertainty.
3. Show time-specific territory coverage for **all six modeled years**, or explicitly limit inferential scope to years with verified source spatial coverage. 2025 must not be inferred from 2024 data without explaining carry-forward uncertainty.
4. Compare CISO topology repair candidates and AZPS/SRP near-contained footprint; characterize sensitivities and do **not** force overlaps into artificial exclusive partitions.
5. State estimand (area-weighted ERA5 vs population/customer/load-weighted exposure), formula, source crosswalk and uncertainty. Audit six-year climate sample availability.
6. Independently approve the metadata/evidence references before setting `geometry_approved=True` in the C2 final join.

**The fully assembled 72-month real-source ERA5/EIA930 panel remains quarantined:** https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989/artifacts/14127710411 . Its correct status is full source engineering completed; historical BA exposure not yet scientifically validated; no predictive GAM/XGBoost skill, ALL/NAT attribution or future SSP/PyPSA results.
