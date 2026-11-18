# C-2 E1 — Real annual retail MWh county support partial identification, 2020–2023 (2026-11-17)

## Purpose and status

Compute **conditional marginal county MWh bounds** from actually observed EIA-861 annual utility–BA–state electricity sales, *not modeled county load*. This is a mathematical support-set diagnostic, NOT an observed or validated allocation and NOT an E2 weather-load model.

Source release **PUDL v2026.10.0**, immutable actual `core_eia861__yearly_sales.parquet` SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`, joined to 933 verified PUDL fixed-release source utility–state–BA–year county FIPS sets from actual [Actions run 44228454642](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44228454642), artifact 14393473675.

Actual successful [GitHub Actions run 44244205677](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44244205677), artifact **14400293606**, downloaded and independently parsed. The workflow verifies that all **16 BA–year actual MWh totals** match independent source-only audit artifact **14400412064** and that the sum of county-specific lower bounds equals the observed annual one-county source MWh.

## Precise **conditional** mathematical interpretation

For reporting source utility–BA–state–year \(u\), let actual observed selected annual retail MWh be \(M_u\ge0\), and set of reported service county FIPS be \(S_u\). If **the reported FIPS list contains every county receiving this electricity, the territory covers these customers and all selected MWh is distributed nonnegatively only to those counties**, define \(x_{u,c}\ge0\) with \(\sum_{c\in S_u}x_{u,c}=M_u\). For \(|S_u|=1\), \(x=M\); for \(|S_u|\ge2\), any particular county has \(x\in[0,M]\). For \(|S_u|=0\), source MWh remains explicitly unlocated. Thus for each \(c\):

\[L_c=\sum_{u:S_u=\{c\}}M_u,\qquad U_c=\sum_{u:c\in S_u}M_u.\]

**Important:** \(L_c,U_c\) are **marginal support-conditional** bounds only; the upper bounds for multiple counties cannot generally hold simultaneously. They are not a lower/upper confidence interval, independent observed demand, or a positive identified spatial weight. A source utility may sell energy as a marketer beyond reported distribution counties; such failures of the assumed support make these mathematical intervals unsuitable as true physical bounds until independently validated.

## Original actual results

| BA | Selected observed annual retail MWh, 2020–23 | One-county conditional MWh | Multi-county not uniquely located MWh | No source county MWh | BA–year–county bound rows | Rows with positive conditional lower |
|---|---:|---:|---:|---:|---:|---:|
| AZPS | 129,057,618 | 4,840,693 (3.751%) | 120,464,912 (93.342%) | 3,752,013 (2.907%) | 56 | 12 |
| BPAT | 207,663,786 | 83,728,317 (40.319%) | 123,932,777 (59.680%) | 2,692 (0.001%) | 416 | 94 |
| CISO | 463,195,807 | 57,723,274 (12.462%) | 389,552,906 (84.101%) | 15,919,627 (3.437%) | 228 | 40 |
| SRP | 124,284,031 | 0 (0.000%) | 123,741,352 (99.563%) | 542,679 (0.437%) | 12 | 0 |
| **Total** | **924,201,242** | **146,292,284** | **757,691,947** | **20,217,011** | **712** | **146** |

There are **566/712** source-supported BA–year–county rows whose marginal lower bound is zero. Even the **146 positive** conditional lower bounds cannot be presented as real physical measured demand unless source service-county completeness holds.

Examples of wide **2023 conditional upper-minus-lower** source support ranges (NOT county demand estimates): CISO San Diego County FIPS 06073 **79,885,331 MWh**; CISO Fresno County 06019 **75,265,862 MWh**; AZPS Apache County FIPS 04001 **31,370,312 MWh**; SRP Gila/Maricopa/Pinal FIPS 04007/04013/04021 each **31,839,865 MWh**. Different county intervals share underlying utility electricity and cannot all take maxima.

## External modeled county hourly benchmark — NOT a verification set

Official DOE/NLR publication *Hourly Electricity Demand Profiles for Each County in the Contiguous United States*, DOI **10.25984/3366592**, https://data.openei.org/submissions/8562 provides estimated county hourly MW for 2016–23, source code https://github.com/NatLabRockies/HistoricalLoadData at observed Git commit **06d09b2a426b8606acae1bbe6edb8bb708c11ecb**. Crucially the county retail allocation is itself estimated using **county population share within state**, and the profiles incorporate reported BA load. It cannot be treated as independent meter-observed county MWh or an independent outcome for BA-derived load. Official metadata documents a **2026-02-09 correction** for a county DPV attribution issue. The actual large HDF5 has **not** been downloaded or used in the present partial-bounds study; any future use must pin actual H5 file SHA256.

## Reproducibility

`src/c2_e1_actual_sales_county_partial_identification.py` preserves the unlocated bucket, generates actual source utility MWh table, 712 marginal county bound rows and 16 BA–year accounting rows. `tests/test_c2_e1_actual_sales_county_partial_identification.py` rejects negative sales and asserts multigeography does not create fake lower weight; workflow `.github/workflows/e1-county-MWh-partial-identification.yml` downloads pinned original data and verifies all 16 independent source MWh totals. Complete output archive: `C2_E1_PARTIAL_IDENTIFICATION_ACTUAL_14400293606.zip`.

## Scientific decision

This is an **E1 source constraints research result** and supports a methods / limitations section; it **does not** pass `GEO_LOAD_RELEVANCE`, `GEO_HISTORICAL_BA_FOOTPRINT` or `LOAD_QUALITY_HOLDOUT_PROTOCOL`. No current county-level MWh observed. `model_training_permitted=false`. C-1 frozen, sealed 2024–2025 hourly EIA-930 demand untouched.
