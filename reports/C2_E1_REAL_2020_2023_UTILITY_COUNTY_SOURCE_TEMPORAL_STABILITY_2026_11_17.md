# C-2 E1 — Real 2020–2023 utility–state county-source temporal stability audit (2026-11-17)

## Immutable original inputs
This is a source-only audit of the *same* original EIA-861 utility–BA association bridge already used for real annual retail-MWh geography coverage. Original [GitHub Actions source bridge artifact 14144934238](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions), 1,418 year–utility–state–BA associations for 2020–2025. Inner `EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv` SHA256 **`957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`**. Only **2020–2023** associations are admitted to this historical stability analysis. No EIA-930 2024–25 sealed hourly demand opened.

Unit of analysis: `BA × utility_id_eia × state` that appears at least once in the 2020–2023 associations. County-source persistence means how many EIA861 reported utility county entries the source bridge contains in each available year. It is **not** a verified customer location or BA service footprint; association may be nonexclusive across BA within utility/state/year.

## Independently calculated actual results

| BA | Unique utility-state entities | Present all 4 years | All observed years zero county entries | Presence switched 0↔>0 | County counts changed in 4-year complete entities | Entities with nonexclusive BA association | Entities with out-of-state counties excluded |
|---|---:|---:|---:|---:|---:|---:|---:|
| AZPS | **27** | **23** | **15** | **0** | **0** | **5** | **0** |
| BPAT | **114** | **108** | **3** | **0** | **0** | **0** | **22** |
| CISO | **105** | **78** | **63** | **1** | **2** | **2** | **3** |
| SRP | **9** | **8** | **7** | **0** | **0** | **5** | **0** |

Additional exact CISO source cases where county-source counts change in a *complete four-year entity*: utility EIA **16612** (CA) counts range **1–2**, and utility EIA **61432** (CA) ranges **0–5**, with utility **61432** demonstrating a real source-presence switch. AZPS and SRP overlap in source association for several utility-state entities; those are **nonexclusive data links**, not verified customer deliveries in both BA. BPAT has **22** utility-state entities with raw out-of-state county entries excluded by the association bridge: retaining only same-state county evidence is conservative about geography, not proof that out-of-state consumption is zero.

**Denominator caveat:** These are counts of utility-state entities in a *source metadata panel*, not percentage of retail MWh or hourly BA demand. 27, 114, 105, 9 are not authoritative BA utility populations. A stable utility county count does not mean its counties or service areas are identical year to year, because the bridge exposes a count, not a full year-specific FIPS mapping.

## Measured retail MWh coverage (independent previous result, unchanged)
For 2020–23 observed bundled annual retail MWh and strict county-source matched share: AZPS **97.0928%**, BPAT **99.9987%**, CISO **96.5631%**, SRP **99.5634%**. These are selected *reporting-source* shares, NOT the share of hourly demand located in the mapped counties. AZPS has ~2.62% of selected sales associated with nonexclusive utility/BA sources, CISO a ~3.43% unmatched-source fraction. Do not promote a high reported-MWh linkage percentage to geographic completeness without actual electricity customer spatial allocation.

## New code and reproducibility
- `src/c2_e1_real_utility_county_temporal_stability.py` verifies frozen 1,418-row bridge and member SHA256 and emits entity detail/4-BA summary/QA JSON.
- `tests/test_c2_e1_real_utility_county_temporal_stability.py` tests source overlap, presence transitions, cross-state exclusion and fail-closed source rejection.
- Workflow `.github/workflows/e1-real-utility-county-temporal-stability.yml` downloads original immutable association artifact and independently runs the same real calculations.
- GitHub Actions [run 44223107462](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44223107462) was **queued** when this report was first composed; do **not** count as independently verified until its conclusion and artifact are checked.
- Local CSV output `C2_2020_2023_REAL_FOUR_BA_GEO_SOURCE_STABILITY_SUMMARY.csv` and `C2_2020_2023_REAL_UTILITY_STATE_GEO_TEMPORAL_STABILITY.csv`, all derived from the hash-pinned original PUDL association bridge.

## Scientific admission
**This does not solve `GEO_HISTORICAL_BA_FOOTPRINT` or `GEO_LOAD_RELEVANCE`.** The next decisive study is year-specific verified county FIPS from original EIA-861 utility service territory *plus actual allocations (customer counts, retail revenue or preferably MWh at county/service territory level)*, independent historical BA boundaries and explicit utility/county overlaps; a population proxy or reporting-source match alone is not sufficient.

`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `GEO_LOAD_RELEVANCE=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`, `model_training_permitted=false`. C-1 frozen; sealed 2024–25 hourly EIA-930 demand not opened.
