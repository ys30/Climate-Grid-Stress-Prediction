# C-2 E1 — Real PUDL null-sector within-filing sibling evidence (2026-11-17)

## Verified empirical source and execution
- Original public PUDL **v2026.10.0** `core_eia861__yearly_sales.parquet`, SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`, pinned in existing workflow.
- Actual completed [GitHub Actions run 44047727588](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44047727588), **SUCCESS**, artifact **14312002877** (downloaded and independently read).
- Relevant full CI [run 44047727655](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44047727655) **SUCCESS**.
- Execution source `src/c2_e1_null_mwh_same_filing_sibling_audit.py`; synthetic tests `tests/test_c2_e1_null_mwh_same_filing_sibling_audit.py`. The source determines a same filing from utility EIA ID, state, report_date, BA, business model, service type; it excludes `total` and requires positive reported sales MWh in a different customer class.

## Actual results: 1,321 eligible original PUDL null sales-MWh class rows

| Customer class | Null sales rows | With another positive-sales class in exactly the same filing grain | No such positive-sales sibling |
|---|---:|---:|---:|
| Other | 709 | **705** | 4 |
| Transportation | 386 | **382** | 4 |
| Industrial | 127 | **123** | 4 |
| Commercial | 52 | **48** | 4 |
| Residential | 47 | **43** | 4 |
| **Total** | **1,321** | **1,301 (98.486%)** | **20 (1.514%)** |

The **20** nulls without another positive sales class come from just **four** utility/state/BA/year report groups, all for **utility_id_eia=59579 in 2025**: AZPS–AZ, BPAT–UT, CISO–CA, SRP–AZ. Each group has 5 null classes (residential, commercial, industrial, transportation and other), no positive class within the matching sales table grain. The underlying rows have null own `customers` and `sales_revenue`, not verified zero MWh.

All **1,301** other null class rows occur in filings for which at least one *different* class has positive sales; thus **they are not equivalent to 1,301 independent utilities or 1,301 unresolved actual positive electric sales amounts**. This is direct source-derived within-record consistency evidence in favor of category-slot interpretation; not an original-Excel proof.

## Actual source ETL mechanism and remaining causality gap

Exactly tagged upstream [PUDL v2026.10.0 `transform/eia861.py`](https://github.com/catalyst-cooperative/pudl/blob/v2026.10.0/src/pudl/transform/eia861.py) calls `_tidy_class_dfs` on sales, which stacks class-suffixed columns via **`data_cols.stack(level=0,dropna=False)`** and retains all-null class slots when transforming wide original filings to the long annual data table. This *mechanism* explains why the resulting long table may contain an unreported class slot with null values even when other customer classes have positive sales in the same report.

This does **not prove** whether each individual original EIA-861 raw wide cell was null/blank, if cells were omitted/standardized by PUDL pre-processing, or whether any null sector represented unreported positive actual electric energy. To resolve original provenance, compare the original archived EIA-861 Sales workbook/fixed raw archive against the PUDL long table for the 1,321 raw keys. No actual raw EIA861 Excel was used in this new result.

## Research implication

Prior conditional sensitivity scenarios adding 5% hypothetically omitted MWh remain algebraically valid but **are not estimates of actual source missingness**; this empirical finding substantially weakens an interpretation based on record count alone. In particular the focus for raw-filing follow-up can narrow to the anomalous 2025 `utility_id_eia=59579` cases and stratified review of non-null sibling filings; not all 1,321 rows need be assumed to represent independent missing source volumes.

Annually matched retail MWh source geography is distinct from *validated customer locations or hour-by-hour BA load exposure*. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain BLOCKED, `model_training_permitted=false`, 2024–2025 sealed **demand** holdout unused, C-1 frozen.
