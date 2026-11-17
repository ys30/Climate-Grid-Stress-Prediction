# C-2 E1: What do the 1,321 missing annual-sales records mean? (2026-11-17)

## Independent original-data result
Source: actually completed [GitHub Actions run 44038797725](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44038797725), artifact 14307784291, PUDL v2026.10.0 Parquet SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`. Actual 407-row grouped record cross-tab input SHA256 `b7f3e7d1d1ddc9258b9f8461324c269d2a92c3758b623b92740532143eddffc4`.

All **1,321** missing-MWh source records were already selected as observed bundled service and non-`total` customer class by the previous staged original data audit. Current new reclassification (actual source record counts, **NOT** amount of MWh):

| BA | Other | Transportation | Industrial + Commercial + Residential | Non-Other total | Missing total |
|---|---:|---:|---:|---:|---:|
| AZPS | 81 | 27 | 39 | 66 | 147 |
| BPAT | 386 | 244 | 80 | 324 | 710 |
| CISO | 208 | 104 | 84 | 188 | 396 |
| SRP | 34 | 11 | 23 | 34 | 68 |
| **Total** | **709** | **386** | **226** | **612** | **1,321** |

**EIA's official annual data page** ([original EIA-861 published history](https://www.eia.gov/electricity/data/eia861/)) specifies **other sector was eliminated in 2003**, with transportation newly separated and the former other-sector activity reassigned to commercial or industrial, as appropriate. This means PUDL's 709 modern `customer_class=other` *null* sales rows are plausible categorical placeholders or normalization artifacts and should **not be equated to missing positive electricity sales** without additional verification against original 2020–2025 EIA form and PUDL ETL. This also does **not** prove 709 structural zero-MWh records. Transportation **is** a legitimate class; 386 records are genuinely null in the source and require investigation. Its absolute MWh impact is unknown.

EIA's data dictionary ([PUDL annual sales](https://data.catalyst.coop/preview/pudl/core_eia861__yearly_sales)) defines `data_observed` as source-observed vs inferred; **observed does not mean every numeric column is non-null**. The current 2020–2025 source audit found 709 other blank records, 386 transportation, 127 industrial, 52 commercial, 47 residential. None may be converted to missing MWh from record counts, and no assumption that each has similar demand is defensible.

## Research consequence
The previously reported conditional coverage curves (e.g., adding an unobserved 5% MWh) remain valid algebraically *as sensitivity scenarios* but cannot be interpreted as likely missing-sales magnitude from the 1,321 row count. **Stratify the QA by class and source reporting semantics before interpreting robustness.**

Confirmed local original cross-tab audit generated 120 BA–year–class rows and 12 BA–period rows; four local regression checks passed. Reproducer: `src/c2_e1_other_class_missing_mwh_source_sensitivity.py` commit `fd1b53ea1a058722311a37f72ce0c694bf10cc13`.

### Next original-source acceptance steps
1. Pin and inspect official EIA-861 primary filing schedule 4 2020–2025 by respondents for missing transportation and regular classes, focusing BPAT and CISO.
2. Compare PUDL `customers`, `sales_revenue`, `short_form`, `data_maturity` and whether rows are ETL-introduced placeholders; this requires actual underlying Parquet or a new Actions artifact. Do not infer from grouped cross-tabs alone.
3. Quantify what proportion of non-other null records have positive customer counts or positive reported sales revenue; **still does not provide MWh** without independent source.
4. Only then revisit conditional MWh bounds, geo-assignment, and E2 admission.

C-1 frozen; E2 GAM/XGBoost, climate attribution and SSP–PyPSA blocked. 2024–2025 sealed hourly **demand** holdout not opened.
