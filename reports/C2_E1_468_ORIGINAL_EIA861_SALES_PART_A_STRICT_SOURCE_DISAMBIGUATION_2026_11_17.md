# C-2 E1 — COMPLETE strict original EIA861 report-row disambiguation for 2020–2023 (2026-11-17)

## Actual original data and source pin

This report improves [the original Excel source-candidate audit](./C2_E1_REAL_RAW_EIA861_2020_2023_SOURCE_CANDIDATE_PROVENANCE_2026_11_17.md), not a new synthetic data collection. The 810 null MWh class rows across the 2020–2023 training/validation split trace to 468 unique year–utility EIA ID–state–BA groups. Original EIA861 Sales original files are pinned to PUDL **v2026.10.0** EIA861 raw archive **Zenodo 23241340**, with year-specific original ZIP MD5 checks applied by the prior successful [workflow 44051874799](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44051874799), artifact **14313717508**.

The previous broad scan found 561 source candidates for 468 groups, of which 49 had multiple candidates. Inspecting the true original values showed that these excess candidates were from Customer Sited, Decoupled, Delivery and otherwise non-target records, **not ambiguous target BA–retail bundled filings**.

## Verified strict original report-row matches

Require:
- Exact archive workbook `Sales_Ult_Cust_<year>.xlsx`, not `Sales_Ult_Cust_CS_<year>.xlsx`.
- Original sheet `States`, not `Decoupled` or `Customer Sited`.
- Original row's year, utility EIA identifier, state and BA all equal to the source group key.
- Original `Part=A`, `Service Type=Bundled`, `Data Type=O` (observed).
- A single candidate remaining for each group; fail closed otherwise.

| Year | Processed null class rows | Unique original source groups | Broad original candidates | Exact Part A/Bundled/O/States original rows | Non-target candidates excluded |
|---|---:|---:|---:|---:|---:|
| 2020 | 200 | 116 | 137 | 116 | 21 |
| 2021 | 184 | 113 | 134 | 113 | 21 |
| 2022 | 195 | 116 | 131 | 116 | 15 |
| 2023 | 231 | 123 | 159 | 123 | 36 |
| **Total** | **810** | **468** | **561** | **468 (100%)** | **93** |

**49/49 previously ambiguous groups now have ONE uniquely identified original source report row; zero unresolved original-row ambiguities.** This is an original filing **row-level** provenance result, not original customer-class **cell-level** proof.

## Reproducibility and CI

- Original source-candidate CSV input SHA256 `1527647b41c22e1e80b9bfd997276fd3c63b9a73b27924439e739f6cd5caf415`.
- Source group inventory input SHA256 `ac59f6534934f60b2a00660edb8395cd908c147d70ae34b7594874fefb9768e7`.
- C2 source `src/c2_e1_2020_2023_strict_raw_sales_disambiguation.py`, tests `tests/test_c2_e1_2020_2023_strict_raw_sales_disambiguation.py`, workflow `.github/workflows/e1-strict-original-sales-disambiguation.yml`.
- Verified [GitHub Actions run 44215715006](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44215715006), **SUCCESS**; artifact **14387478090**, CSV SHA256 `eda59eaa015fd0cf4eaedb73cb73bda06a1c1fd13d6ba7e72adbd249c8b0ba91`.
- Local *independent* pandas merge of the GitHub original-row CSV against separately computed original Excel disambiguation 468-row CSV found **0 original row-number mismatches and 0 original raw-row SHA256 mismatches**, matched on all 468 source group identifiers.
- Seven explicit regression tests guard against accepting Customer Sited, Delivery, Decoupled, imputed data, wrong state or wrong BA.

## Remaining scientific work (do not overclaim)

This confirms the **identity of the original row** for every group, not a quantitative statement about the original raw revenue, sales MWh, or customer-class cell. Next construct the year-specific original column maps and reconcile exact original sector triple values (revenue, sales MWh, customers) for all 810 processed null-sector rows. A literal `.` remains missing/not stated, never automatically numeric zero.

Even after original annual Sales source cell lineage is complete, **source county association is not actual geographic electricity consumption**: the `GEO_HISTORICAL_BA_FOOTPRINT` and `GEO_LOAD_RELEVANCE` gates still require validated service-territory allocation and weather spatial weights. `LOAD_QUALITY_HOLDOUT_PROTOCOL` remains blocked, `model_training_permitted=false`; no sealed EIA930 2024–25 hourly demand accessed; C-1 frozen.
