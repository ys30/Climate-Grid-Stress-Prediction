# C-2 E1 — Temporal BA member admission and source-honest CEC 1305/1306A join (2026-11-24)

## What changed in code

The existing [CEC 1305/1306A joint-source inspector](../scripts/c2_cec_joint_geo_source_gate.py) now requires a **new explicit normalized field**, `membership_effective_whole_month`, in every control-area membership row.

- `True`: only *declares* whole-month membership in a candidate normalized record; even with unique BA membership and a reviewed UDC→EIA identifier, the resulting county×BA GWh remains a conditional source-association candidate **and is never an approved load weight**.
- `False`: if a reporting UDC joined/left a control area during the month, or the source identity cannot certify whole-month applicability, *all consumption for that UDC/month* is kept out of the candidate assignment and counted under `membership_partial_month_unresolved`. This conservative classification takes priority over apparent uniqueness or multiple-BA categorization.
- Empty/malformed flag: **reject the input**, rather than assume year/month membership is valid all month.

The previous revisions also reject duplicate normalized consumption grains `(year,month,county_fips,udc_id,sector)`, duplicate membership, source SHA mismatches, missing/negative GWh, unreviewed identifiers, and multi-BA association. None of these checks turns member identity or a delivery total into an observed operating BA footprint or geolocated hourly demand.

## Test evidence and limits

- 10 committed test methods now exist in `tests/test_c2_cec_joint_geo_source_gate.py`, including two new month-effective date cases.
- An **independent local equivalent implementation and fixture harness** was actually run with Python 3.13: **11/11 local tests passed** (including a separate explicit multi-BA check). The local mirror uses the same relevant algorithms and test cases, but is **not byte-for-byte identical** with the GitHub repository files.
- A push/PR CI workflow already exists at `.github/workflows/c2-cec-joint-geo-contracts.yml` and should discover the committed tests. GitHub Actions success was **not independently confirmed during this turn**, so do not label CI green.

## Source provenance still missing

CEC [forms and instructions](https://www.energy.ca.gov/resources/forms/forms-instructions-reporting-electric-and-natural-gas-sales-and-electric) identify 1305A/B/C control area reports; the existing C-2 source memo identifies [CEC QFER consumption](https://www.energy.ca.gov/rules-and-regulations/energy-suppliers-reporting/quarterly-fuel-and-energy-reporting-qfer) as the second source lead. But **no authenticated actual month-effective CEC 1305 / county×UDC 1306A joint rows** were fetched, and the program's self-declared `source_kind=official_original` is **not proof of external provenance**. A separately authenticated raw release, raw→normalized field lineage, confidentiality/license assessment, and independently reviewed dates and IDs remain mandatory before scientific approval.

For any mid-month UDC join/leave, monthly GWh is **not** allocated pro rata by days or copied into either BA; an independent hourly/submonthly actual source would be needed to do so.

## Scientific status

`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`; `GEO_LOAD_RELEVANCE=BLOCKED`; `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`; `model_training_permitted=false`. The 2018 HIFLD BA exposure candidate remains exploratory; 2020–25 six-year ERA5/EIA archive is genuine source data but not approved as a model input. No demand model, climate attribution, SSP/CMIP6 projection or PyPSA adequacy results are inferred. C-1 unchanged.
