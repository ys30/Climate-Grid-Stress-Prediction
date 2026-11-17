# C-2 E1 — REAL PUDL 2020–2025 eligible bundled missing-sales MWh classification, 2026-11-17

**New successful empirical run:** [GitHub Actions 44038797725](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44038797725) completed **successfully**, artifact **14307784291** downloaded and source output independently analyzed. [Whole-contract CI 44038797768](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44038797768) also passed. Source immutably pinned to original PUDL v2026.10.0 `core_eia861__yearly_sales.parquet` SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`.

## Real sequential exclusion of all 5,180 records for four BAs, 2020–2025

| Category | Original row count |
|---|---:|
| Not data_observed | 350 |
| data_observed, service_type != bundled | 1,285 |
| Observed bundled eligible customer class, sales_mwh missing | **1,321** |
| Observed bundled eligible customer class, sales_mwh available | **2,224** |
| **Total** | **5,180** |

**No other/aggregate unknown customer class was excluded in this source**; this is an actual source observation, not a claim that all source classifications have complete valid retail-sales meaning.

| BA | Eligible missing MWh rows 2020–2023 | Eligible missing MWh rows 2024–2025 | Total missing | Total eligible nonmissing | Missing row percentage |
|---|---:|---:|---:|---:|---:|
| AZPS | 78 | 69 | 147 | 258 | 36.30% |
| BPAT | 472 | 238 | 710 | 1220 | 36.79% |
| CISO | 233 | 163 | 396 | 644 | 38.08% |
| SRP | 27 | 41 | 68 | 102 | 40.00% |
| **Total** | **810** | **511** | **1321** | **2224** | **37.26%** |

## Strong actual missingness structure by customer class

| Original `customer_class` | Missing MWh rows | Nonmissing MWh rows | Missing-row share |
|---|---:|---:|---:|
| other | **709** | **0** | **100.0%** |
| transportation | **386** | **323** | 54.44% |
| industrial | 127 | 582 | 17.91% |
| commercial | 52 | 657 | 7.33% |
| residential | 47 | 662 | 6.63% |

**82.9%** of missing-MWh rows are in `other` or `transportation` (1095/1321), while all `other` rows are missing MWh across AZPS/BPAT/CISO/SRP in the actual source filter. This is structured missingness, not randomly distributed records. **It does not establish that other-class retail MWh is zero, that all records correspond to customers with electricity use, or that their unknown volumes equal a fraction of annual sales.** Never substitute row-count weights for energy weights.

## Interpretation and follow-on identification work

The verified sales-country-source coverage is conditional on 2,224 **nonmissing** annual retail-sales rows, not an unconditional BA hourly-demand coverage statement. The 1,321 unknown MWh **cannot** be assigned numerical totals, and no actual missing MWh volume has been measured. Next scientific QA should examine EIA-861 service/class reporting semantics and original utility-year filings for `other` and `transportation` before changing the denominator or imputing anything; differentiate structural NA from genuine non-reporting using utility-level source references.

The actual result output includes `C2_E1_MISSING_MWH_BA_YEAR_STAGE.csv` and `C2_E1_MISSING_MWH_BY_SERVICE_CLASS_BUSINESS.csv`, plus class/BA summaries and SHA manifest in local artifact `C2_E1_REAL_MISSING_MWH_CLASSIFICATION_20261117.zip` SHA256 `b5a076f6c50f40d53f4ec40e337b3b71a830ff52f73ce4acaf99cf1efdb814de`.

**Science admission remains BLOCKED** (`GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL`; `model_training_permitted=false`). No 2024–2025 EIA-930 sealed demand test values were used. C-1 remains frozen.
