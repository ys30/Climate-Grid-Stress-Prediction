# C-2 E1 — Verified real customer/revenue evidence for 1,321 null annual-sales records (2026-11-17)

## Empirical verification

Previously pinned PUDL v2026.10.0 `core_eia861__yearly_sales.parquet` SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`. Actual [GitHub Actions run 44043460975](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44043460975) **success**, artifact **14310951946**, with new `C2_E1_MISSING_MWH_CUSTOMER_REVENUE_BY_BA_CLASS.csv`, `C2_E1_MISSING_MWH_REPORTING_EVIDENCE_STRATA.csv` and QA JSON. The overall `phase1-ci` run **44043461040** is also successful.

Original empirical result for **1,321** null sales-MWh records filtered to 2020–2025, four BA, `data_observed=true`, bundled, non-total recognized customer classes:
- **1,318** rows have **both `customers` and `sales_revenue` null**, in addition to missing `sales_mwh`;
- **3** rows have **null `customers`, reported `sales_revenue=0`**, missing `sales_mwh`: **BPAT–2020–transportation (two records)**, **CISO–2024–transportation (one)**;
- **0** rows show `customers>0`, `sales_revenue>0`, either positive, both positive, negative customers/revenue, or nonfinite numeric sources;
- all 1,321 show `data_maturity=final`; all 1,321 have null `short_form`. Blank `short_form` is *unknown*, not proof of false.
- Actual class totals are **other=709**, **transportation=386**, **industrial=127**, **commercial=52**, **residential=47**. By BA AZPS=147, BPAT=710, CISO=396, SRP=68.
- The underlying grouped evidence is independently decoded from the successful artifact; output CSV SHA256: BA-class `2fd58e168cad805e879a54713a662cf301420a74e22b8f2ba4558fc142ae8f72` and reporting strata `5c97772cc550560fcb21b949327ceeb69e13f3b0d61903299733f690b8620bae`.

## Interpretation

There is **no positive customer or revenue evidence** within these 1,321 null-MWh source records. This makes a naive assumption that all blank rows are unmeasured positive retail MWh unsupported, and is consistent with potentially structural or not-applicable combinations. **It does not prove each missing MWh represents zero** and it does not validate the true sector reporting rules, short-form source semantics, or utility hourly load geography. The previously presented missing-5%-MWh sensitivity remains **purely conditional**, not a confidence interval or estimated missing energy. The EIA-861 historical `other` customer category is discontinued, but individual PUDL placeholders are not yet independently verified structural.

## What changed in scientific gate?

Annual observed bundled MWh geography-source matching is still available (2020–2023: AZPS 97.0928%, BPAT 99.9987%, CISO 96.5631%, SRP 99.5634%) based on true EIA861 sales; however annual retail sales having a mapped utility/county source is **not** a verified county/cell allocation of demand, and the 2024–2025 sealed hourly demand test has not been opened. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE` and `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain **BLOCKED**; `model_training_permitted=false`; C-1 frozen.

## Next decisive evidence

1. Establish original EIA861 sector filing or PUDL ETL provenance for the 709 `other` and 386 `transportation` null slots and source utility identities; determine whether the rows were instantiated as not-applicable defaults.
2. Independently build/verify actual utility-to-county sales or meter/customer allocation (not a guessed population-weighted county proxy) for the annual MWh panel, explicitly distinguishing multi-BA utility associations.
3. Only after source validity and spatial relevance gates can historical weather–load response and future SSP–PyPSA simulations be considered.
