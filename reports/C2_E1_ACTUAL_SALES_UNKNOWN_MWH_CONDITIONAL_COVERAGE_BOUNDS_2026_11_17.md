# C-2 E1 — Conditional missing-retail-MWh coverage sensitivity (2026-11-17)

**New real-source-derived result.** Actual sales denominator and strict matched numerator are from the 24-row verified PUDL v2026.10.0 annual EIA861 source report, SHA256 `2b437b6288e1d8221aa555c63aadfbf16d033406b4ac5ee6c70bff0d497987c0`. Original PUDL Parquet SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`. Sources independently reproduced in GitHub Actions 44032717255, 44031912206 and SHA-pinned 44037370237.

## Estimand and honest missingness treatment

In the verified current filter, 2,224 observed bundled/non-total records yielded retail MWh, while 1,321 rows had missing sales_mwh (sequential exclusion). Their actual aggregate MWh are unknown. Let D=selected observed annual retail MWh, N=its strict county-source-associated MWh, U=**hypothetical additional eligible retail MWh** not yet accounted for. Conditional worst-case share = N/(D+U) if none of U has a county source; conditional best-case share = (N+U)/(D+U) if all of U has a county source. These formulas do not estimate actual U and are **not unconditional empirical confidence bounds**. No missing source MWh was imputed.

## Actual 2020–2023 selected-sales baseline and conditional extra 5% MWh scenario

| BA | Observed selected MWh | County-source matched observed MWh | Baseline percent | All extra unmatched percent | All extra matched percent |
|---|---:|---:|---:|---:|---:|
| AZPS | 129,057,618 | 125,305,605 | 97.0928 | 92.4693 | 97.2312 |
| BPAT | 207,663,786 | 207,661,094 | 99.9987 | 95.2369 | 99.9988 |
| CISO | 463,195,807 | 447,276,180 | 96.5631 | 91.9649 | 96.7268 |
| SRP | 124,284,031 | 123,741,352 | 99.5634 | 94.8222 | 99.5842 |

The *hypothetical* extra all-unmatched MWh divided by current observed D needed to reach **95%** strict source-associated coverage is 2.20291% (AZPS), 5.26179% (BPAT), 1.64536% (CISO) and 4.80353% (SRP). These are mathematical vulnerability thresholds, not observations about excluded MWh.

## Reproducibility and next data demand

Local independently executed Python computation verified the 24-row input SHA and produced a 48-row (2 periods × 4 BA × 6 conditional missing MWh fractions) CSV and 32-row coverage-breakpoint CSV. Source code `src/c2_e1_real_sales_unknown_mwh_sensitivity.py` committed in `86150e9203d2296668c88c3e0ca4983e7b3ee951`. Complete downloadable local source/results/report package `C2_E1_ACTUAL_SALES_MWH_UNCERTAINTY_BOUNDS_20261117.zip` SHA256 `1ac1360e29bbd9b8eec3d30cd0fc39a27a6cf296c8c695b884361920da449780`.

**Next decisive evidence:** inspect the 1,321 missing-sales records by BA/year/customer_class/service_type/business_model and determine whether the selected denominator systematically undercounts sales by particular operators; do NOT assume all are missing retail MWh without inspecting original filter stages. Independent utility meter geography is still needed before creating county/grid-cell hourly load-exposure weights. `model_training_permitted=false`; E2 GAM/XGBoost, climate ALL/NAT and future SSP/PyPSA stress not done. C-1 remains frozen. 2024–2025 demand holdout untouched.
