# C-2 E1: VERIFIED official CEC QFER workbook margins; joint county-by-agency sales NOT identified

**Verification date: 2026-11-21.** Source interpretation audit only. C-1 frozen;
C-2 E2 model admission remains blocked.

## Independent empirical evidence, not merely a queued workflow

[Official CEC workbook source-schema run 44872398200](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44872398200)
completed **SUCCESS**. Its actual source-structure JSON artifact **14695445486**
was downloaded and independently inspected. Original CI JSON SHA256:
`19dd37863086d4981290a9e15130ae5c77ca9071b23c3edb09d1723ca99250ec`.

Two source workbook identities from actual GitHub CI downloaded bytes:

| Actual official file | Original XLSX SHA-256 | Excel extent |
|---|---|---|
| `AGG_CONSUMPTION_ELEC_COUNTY_TBL_ada.xlsx` | `142a104d6deebc5c789c1dfcc51387f8681891e4e300f787510cf8b7c23d67ca` | `A1:F14169`, one sheet |
| `AGG_CONSUMPTION_ELEC_UTILITY_TBL_ada.xlsx` | `b2a8a8d5863cca938ce3cf6c41c6ff941c20640a977952e75e449732f19460c2` | `A1:G11460`, one sheet |

**Exact Excel first-row headers independently extracted:**

- County workbook: `YEAR, COUNTY_NUM, COUNTY_NAME, SECTOR, RNR, GWH`.
- Utility workbook: `YEAR, PLANNING_AREA, AGENCY_NAME, AGENCY_TYPE, SECTOR, RNR, GWH`.

These two released sheets have **no individual observation containing both
a county ID and an agency ID**. That is a direct source-structure fact.
An agency-by-county electricity matrix is **not** observed in either file.
This does NOT prove that other California public data products or original
QFER 1306A respondent submissions cannot contain such a joint dimension.

## Fundamental identification argument

Let unobserved electricity consumption for agency `u` and county `c`
be `x[u,c] >= 0`. Released county sums are
`C[c] = sum_u x[u,c]`, and released agency sums are
`U[u] = sum_c x[u,c]`. Even **if** their accounting scopes, years,
sector definitions and total consumption matched exactly, these
marginals generally do NOT determine unique `x[u,c]` values.
For two counties and two agencies with positive off-diagonal support,
shifting a small `epsilon` around their four cells preserves
every county and agency total while altering every joint allocation.
An official utility service-area county list narrows structural zeros
but is not a measured physical electricity load fraction.

Additionally, CEC QFER consumption includes categories outside EIA861
selected bundled retail sales, and a distribution agency need not
equal CISO EIA-930 balancing authority membership. Neither
annual marginal series is measured hourly load-exposure geography.

## Potential upstream joint source, not yet obtained

CEC official QFER 1306A Schedule 1 filing instructions explicitly require
reporters to supply the **county number where the end-use customer
consumed reported electricity**. Official source:
https://www.energy.ca.gov/sites/default/files/2025-07/1306A_Instructions_07142025_ada.pdf

The relevant California public dataset:
https://publish.data.ca.gov/dataset/california-electricity-consumption-dashboard
has documented temporal coverage 1990–2024, and metadata updated in
2026. A website update does not imply verified 2025 electricity observations.

**Open evidence request:** ask the CEC QFER Energy Assessments Division,
contact `QFERDemand@energy.ca.gov`, whether historical
2020–2023 original or confidentiality-compliant aggregated
`YEAR × COUNTY_NUM × UDC/AGENCY × SECTOR × electricity GWh`
is publicly accessible, downloadable, subject to disclosure controls,
and if compatible with actual utility territory/electricity delivery
scope. Do NOT claim access to respondent-level private reports.
A response would still require an independently verified CISO/EIA930
BA-to-agency crosswalk and seasonal/hourly load exposure assumptions.

## Machine-checkable provenance and gate

- `scripts/c2_cec_verified_marginal_only_admission.py` accepts the
  SHA-pinned actual original CEC CI artifact, verifies both original
  workbook digests and exact headers, and refuses to admit county/agency
  joint data.
- `tests/test_c2_cec_verified_marginal_only_admission.py`: synthetic
  regression tests for altered original schema, SHA changes and false
  geographic admission.
- `.github/workflows/c2-cec-verified-margins-admission.yml`: new
  independent actual source-evidence CI. Its result is unconfirmed
  until the exact run finishes.

Previously verified EIA861 actual retail source totals for 2020–2023
remain **924,201,242 MWh**, with **757,691,947 MWh** reported under
multiple county support labels, not uniquely allocatable to county.
No actual EIA861 sales source re-download was required or performed.

**GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED**
**GEO_LOAD_RELEVANCE=BLOCKED**
**LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED**
**model_training_permitted=false**
No ALL/NAT attribution or SSP stress forecast.
