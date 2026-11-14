# C2 E1 — first CI-verified real full-month ERA5 × EIA-930 source audit

Audit date: 2026-11-13 / 2026-11-14 UTC.

## Success: 2020 and 2025 July (31 days each)

CI https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563497776 : **both month jobs SUCCESS**, original EIA-930 source demand matched with actual ARCO ERA5 2-meter temperature hourly 0.25° cells, using the four full experimental BA area-weight masks.

| Year | Actual ERA5 BA-hours | Hourly EIA load records paired | Missing original EIA demand hours | EIA anomaly candidate flags |
|---|---:|---:|---:|---:|
| July 2020 | 2,976 / 2,976 | 2,952 | 24 | 0 |
| July 2025 | 2,976 / 2,976 | 2,974 | 2 | 2 |
| **Total** | **5,952 / 5,952** | **5,926** | **26** | **2** |

The detected original EIA-930 missing-demand episodes were not filled or inferred:
- SRP, 2020-07-11T07:00:00+00:00 through 2020-07-12T06:00:00+00:00 (**24 consecutive hourly missing demand values**).
- SRP, 2025-07-07T06:00:00+00:00 (**1 missing demand hour**).
- SRP, 2025-07-10T07:00:00+00:00 (**1 missing demand hour**).

Note: 2 anomaly candidate flags in 2025 are additional BA-hour QA candidates, not necessarily measured errors; the present manifest has no per-flag assertion of error mechanism. **The 2,974 technically paired July 2025 hours are not automatically model-eligible**.

Both CI artifacts persist with source and weight hashes:
- 2020: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563497776/artifacts/14101446706 ; zip SHA256 `190aa0b9c9607393a7fa7fe691a346572c7086717108c8c63479f8b9e03e9d11`.
- 2025: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563497776/artifacts/14100889865 ; zip SHA256 `6f8e34d08043005812efc2dd152680313da7286ae3b32dd20e3b67e47a7b7cee`.

Observed BA-hour slots per month are exactly 31 × 24 × 4 = 2,976, derived from ERA5 0.25° gridded observations in each BA's experimental area mask (AZPS 265, BPAT 1557, CISO 662, SRP 55 weighted cells), with no interpolation. These are complete **weather data for the two sampled Julys**, not validated complete 2020–2025 calendar-year climate records.

Frozen unapproved polygon-grid weighting CSV SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.

## Geographic and modeling restrictions

National source control-area polygons carry `YEAR=2018`; three original polygons had invalid topology, and CISO geometry `make_valid` changed the raw projected area calculation by ≈7.08%. Derived AZPS and SRP masks overlap ~96.66% of SRP mask area. These must be individually reviewed before admitting BA area-weighted weather as BA-representative model predictors. All per-row training / validation eligibility remains **FALSE**. No causal anthropogenic climate attribution or future SSP stress outcome was estimated.

The existing E0 whole-year source-coverage check is independent; it does **not** approve weather exposure or model training.

## Remaining July source years

The independent full-July audit across 2021, 2022, 2023, 2024 was submitted:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/workflows/e1-real-monthly-2021-2024.yml

The 2021–2024 runs are not included in any observed-result count until their CI jobs and artifacts complete successfully.

## Next E1 requirements

Continue full-month source acquisition across cold / transitional seasons with provenance, audit yearly demand anomalies/missingness and obtain an independent geographic-mask source-vintage and overlap review. Only after full 2020–2025 weather coverage and geography approval should chronological calendar/GAM/XGBoost evaluation begin.


## Completed: real July monthly audits for all six years 2020–2025

Four remaining source-month jobs succeeded (2021–2024):
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563639298

Independent six-monthly-manifest reconciliation also **SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563853479

| July source year | Real ERA5 BA-hour observations | Observed EIA–ERA5 complete BA-hours | Original EIA930 demand missing | Source anomaly *candidates*, not confirmed bad values |
|---|---:|---:|---:|---:|
| 2020 | 2,976 | 2,952 | 24 | 0 |
| 2021 | 2,976 | 2,976 | 0 | 1 |
| 2022 | 2,976 | 2,976 | 0 | 3 |
| 2023 | 2,976 | 2,976 | 0 | 3 |
| 2024 | 2,976 | 2,976 | 0 | 0 |
| 2025 | 2,976 | 2,974 | 2 | 2 |
| **Total** | **17,856** | **17,830** | **26** | **9** |

Every July contains 31 × 24 hours at four BAs, real gridded public ARCO ERA5 observations with frozen area-weight candidates. All original demand gaps were retained as missing and excluded from the **complete pair count**, not interpolated. **Anomaly flags are additional suspect values that require review even if a paired temperature and nonmissing demand are present; 17,830 must not be represented as eligible clean rows.**

Independent source QA reconciliation verified exactly six distinct 31-day source manifests, 2,976 real weather slots in each, identical geometric weight input digest, no imputation, and all geographic/model approval flags false.

CI output: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563853479/artifacts/14101635987 ; artifact SHA256 `c4cf97d859d4a6859874c6edb8021e981baa69c1814c96ac25d8da119c95f7ff`.

2021–2024 individual monthly archive artifact IDs:
- 2021 `14101273997`; 
- 2022 `14101561340`;
- 2023 `14101925186`;
- 2024 `14101561494`;
on https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563639298 .

**No full calendar year (January–December) has been extracted and approved yet.** These six real Julys establish reproducible one-month seasonal coverage only. All area exposure masks are 2018-vintage, post-topology-repair provisional masks, with the same known source-admissibility issues: CISO geometry ~7.08% raw-area sensitivity and AZPS/SRP ~96.66% SRP polygon overlap. Source EIA-year coverage is separately audited in E0. No GAM/XGBoost forecast or causal anthropogenic attribution is authorized.
