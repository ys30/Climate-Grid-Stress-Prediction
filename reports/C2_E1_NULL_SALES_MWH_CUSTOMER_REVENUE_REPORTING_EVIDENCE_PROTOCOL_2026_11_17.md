# C-2 E1 — Null-sales MWh: customer, revenue and short-form reporting evidence (2026-11-17)

**New source-pinned original-data audit submitted; actual positive-customer/revenue counts not yet verified until the queued workflow completes.**

## Grounded source and rationale

The successfully used PUDL v2026.10.0 annual sales original Parquet has SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`. Its 2020–2025 AZPS/BPAT/CISO/SRP 5,180 source records include exactly 1,321 observed bundled non-total records with null MWh (709 other, 386 transportation, 127 industrial, 52 commercial, 47 residential) under our frozen source-only filter. Independent [PUDL official schema](https://data.catalyst.coop/preview/pudl/core_eia861__yearly_sales) verifies annual `sales_mwh`, `customers`, `sales_revenue`, `short_form` and `data_maturity`. Annual retail sales missingness is **not** evidence of equally sized missing megawatt-hour volumes.

## Newly executable empirical audit

- `src/c2_e1_null_sales_customer_revenue_evidence.py` scans the exact original Parquet after SHA256 check and requires the complete original null-class counts (1,321 total). It emits `C2_E1_MISSING_MWH_CUSTOMER_REVENUE_BY_BA_CLASS.csv` with BA/class source counts, counts of positive customers, positive revenue, both/either, both missing, negative/revenue-quality anomalies and short-form reporting status; `C2_E1_MISSING_MWH_REPORTING_EVIDENCE_STRATA.csv` separates BA/year/class/short-form/data maturity/customer-state/revenue-state with counts. Missing, zero, positive, negative and invalid numeric sources are not conflated.
- `tests/test_c2_e1_null_sales_customer_revenue_evidence.py` has seven synthetic test cases for strict eligibility and customer/revenue states, integrated into the tagged-source workflow.
- `.github/workflows/e1-eia861-sales-geography-coverage.yml` runs the new tests and true evidence audit against the same 2026.10.0 Parquet SHA pin, uploads outputs to the existing source-only artifact alongside annual MWh coverage.

Latest code revision `a0f73e76b068bebfb8469ba92eb77303993f5744` avoids wrongly treating negative revenue adjustments as necessarily corrupt. Github Actions [run 44043460975](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44043460975) was **queued** when checked; report no actual BA/class positive customer/revenue tallies until that run or equivalent is successful and outputs inspected.

## Scientific interpretation and acceptance

Positive `customers` and/or `sales_revenue` on a null-`sales_mwh` row is **a source reporting anomaly requiring original EIA-861 filing review**, not automatically a positive missing MWh estimate. Historical discontinued `other` classification remains *possibly structural* but **not verified zero**; no imputation or resolution is implied. The 612 non-other blanks require further investigation, with BPAT transportation and CISO transportation/industrial prioritized. Any negative revenue or invalid values must be reported as anomalies rather than converted into electric demand. Do not simply sum associated retail customers across years as unique persons.

The source-only E1 actual sales geographic-association coverage results previously verified (2020–23 AZPS 97.0928%, BPAT 99.9987%, CISO 96.5631%, SRP 99.5634%) are unchanged by this new null-data classification program. None verifies county load allocation or hourly grid stress. `model_training_permitted=false`; C-1 remains frozen; sealed 2024–25 EIA-930 demand test untouched.
