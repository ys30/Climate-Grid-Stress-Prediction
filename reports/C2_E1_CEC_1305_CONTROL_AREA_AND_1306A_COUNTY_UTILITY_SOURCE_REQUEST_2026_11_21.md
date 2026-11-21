# C-2 E1/E2 — CEC dual-source evidence pathway: control-area membership AND county×utility consumption

**Research date:** 2026-11-21. **Original data request not yet sent.**
This is an official-document corroborated evidence-acquisition plan, NOT an observed new join or a model result. C-1 frozen.

## 1. Already confirmed original empirical sources

- Original CEC annual county and agency workbook extraction / SHA verification,
  [Actions 44872398200](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44872398200)
  and independent no-joint-allocation admission [44907545655](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44907545655):
  the county sheet has `YEAR, COUNTY_NUM, COUNTY_NAME, SECTOR, RNR, GWH`,
  the agency sheet `YEAR, PLANNING_AREA, AGENCY_NAME, AGENCY_TYPE, SECTOR, RNR, GWH`.
  Neither released sheet alone has county×agency joint rows.
- PUDL v2026.10.0 SHA-pinned EIA861 annual retail sale results
  (`reports/C2_E1_ACTUAL_924M_MWH_COUNTY_PARTIAL_IDENTIFICATION_BOUNDS_2026_11_17.md`):
  2020–23 selected annual retail MWh 924,201,242;
  757,691,947 MWh in ambiguous multiple-county source sets.
  This is not county-observed hourly BA demand.

## 2. NEW official CEC document finding: Control Area Operator CEC-1305A/B/C

Official CEC **Forms & Instructions for Reporting Electric and Natural Gas
Sales and Electric Generation Information**:
https://www.energy.ca.gov/resources/forms/forms-instructions-reporting-electric-and-natural-gas-sales-and-electric

Under **Control Area Operators Serving California**, CEC lists form
CEC-1305A, CEC-1305B, CEC-1305C. CEC explicitly says these reports
provide *monthly system peak demand and hourly load in each California
control area*, and also *list utility distribution companies (UDCs) in
each control area, interconnections and interchanges with adjacent
control areas, and changes when UDCs join/leave a control area*.
Historical reports are due monthly. This is an original
reporting-mechanism **source lead**, not proof that all 2020–25
machine-readable respondent filings are public or that the historical
CEC control-area definition matches EIA-930 BA demand.

**Critical scientific potential:** Original historical 1305 utility
membership and month-specific entry/exit changes could establish a
date-qualified CISO-to-UDC mapping, subject to original release
verification and reconciliation against EIA BA IDs and its operating
scope. It cannot independently identify county load weights.

## 3. Independent 1306A joint consumption source inquiry

Official CEC **QFER Consumption Data**:
https://www.energy.ca.gov/rules-and-regulations/energy-suppliers-reporting/quarterly-fuel-and-energy-reporting-qfer

It states QFER 1306A UDC consumption submissions generally include year,
month, customers, revenues, sales/deliveries, reporting county, NAICS.
The original filing contains more dimensions than the two downloaded
public annual marginal XLSX workbooks. CEC's public catalog dataset:
https://publish.data.ca.gov/dataset/california-electricity-consumption-dashboard
records temporal coverage **1990–2024** and publisher update
**November 10, 2026**; an updated catalog timestamp is NOT confirmation
of 2025 actual records.

Question for source custodian: Is it possible to obtain **publicly
releasable aggregate** (subject to confidentiality screening) observations
for 2020–2023, ideally 2024 if available, with
`YEAR, MONTH (optional), COUNTY_NUM, DISTRIBUTION_UTILITY_AGENCY_ID,
SECTOR, TOTAL_DELIVERED_GWH, SELF_GENERATION_GWH if separately reported`?
This data is needed to test identifiability but should not be treated as
EIA861 bundled retail MWh unless accounting definitions are reconciled.

## 4. Official data contacts (do not confuse reporting portal access with public-research access)

- CEC public *California Electricity Consumption Dashboard* catalog
  explicitly lists **QFERDemand@energy.ca.gov** as data contact;
  preferred first contact for public aggregate data existence, access
  rights and disclosure criteria.
- The CEC *QFER consumption reports* administrative/filing page lists
  **QFERconsumptionDSP@energy.ca.gov** for report submissions, portal
  access and assistance. It is **not** a reason for a researcher to seek
  an authorized respondent-only reporting account.
- The CEC forms page lists **QFERGEN@energy.ca.gov** under 1305
  Control Area Operators. Request archival 1305A/B/C control area
  membership/hourly data **availability, public release policy,
  schema and metadata**, not private credentials.

## 5. Two requests, two independent scientific gates

| Original evidence request | Scientific issue | Cannot establish alone |
|---|---|---|
| CEC 1305A/B/C date-qualified BA/UDC membership | Crosswalk of CISO BA identity and actual utility participation over 2020–25 | County-level load allocation or metered customers |
| CEC 1306A nonconfidential year×county×UDC×sector GWh | Actual agency-specific county consumption support | Historical CISO operational BA reporting membership or hourly weather-response weights |

**Do not infer a joint distribution from margins**; do not assign missing
county MWh using only population weights and claim observed meter data.
Do not treat modeled NLR population-based county hourly profiles as
independent CISO ground truth.

## 6. Requests, approvals and empirical workflow not yet completed

1. Confirm which 1305A/B/C historic respondent records are accessible,
   whether a public archive exists, and original definitions for BA
   membership and effective reporting time.
2. Confirm CEC 1306A public county-by-UDC source availability with
   confidentiality and aggregation rules; don't request suppressed cells.
3. Save original release/version, byte hashes, source URL/license,
   year coverage and field definitions before applying a linkage.
4. Use utility source identifiers and year/month to map actual CEC
   reporting identities to PUDL EIA861/EIA930. Reject unknown and
   nonunique mappings explicitly.
5. Compare annual county×UDC totals with separately released CEC
   marginals **only for genuinely matched scope/sector/year**; never
   treat equality as evidence of unique true physical BA support.
6. Only after source independent review consider updating the
   scientific gates. This memo and source lookup do **not** clear them.

**Gate status:**
`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`;
`GEO_LOAD_RELEVANCE=BLOCKED`;
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`;
`model_training_permitted=false`; C-1 untouched.
