# C-2 E1 — PUDL v2026.10.0 *exact tagged-source* audit: structural null-row creation mechanism (2026-11-17)

## What is independently confirmed (not just an explanation of the schema)

The original code for **the same fixed PUDL release** used to produce the real EIA861 sales Parquet can be directly inspected at:
- [Tagged v2026.10.0 `src/pudl/transform/eia861.py`](https://github.com/catalyst-cooperative/pudl/blob/v2026.10.0/src/pudl/transform/eia861.py)
- Original source `_tidy_class_dfs`, explicitly called by `core_eia861__yearly_sales`: it turns wide class-suffixed reporting columns into long `customer_class` records, executing **`data_cols.stack(level=0, dropna=False).reset_index()`**.
- This `dropna=False` choice means **an all-null customer-class slot may remain a long-format source row** rather than disappearing. `_tidy_class_dfs` can also consolidate duplicate keys, and `core_eia861__yearly_sales` deduplicates and converts revenue from thousands to dollars and `data_observed` O/I to boolean.

**Synthetic executable mechanism proof:** `tests/test_c2_e1_pudl_2026_10_wide_long_null_mechanism.py`, commit `c591f9f398dfbb8e18e1ab69ad7c07cbfdd3f54c`, uses a single original wide mock utility row with residential sales/customers and no reported other sales/customers. With the tagged transformation operation, a second `customer_class=other` record is created containing *both values null*. This mechanism test has been **executed successfully locally on pandas 2.2.3**, before GitHub commit CI is verified.

## Relation to actual frozen empirical results

Actual previously verified PUDL v2026.10.0 annual sales Parquet SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`. Successfully executed original source customer/revenue audit [GitHub run 44043460975](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44043460975) found **1,321** null-sales rows in the selected observed bundled/non-total four-BA 2020–2025 subset. Of these:
- **1,318** have null customers and null revenue as well;
- **3** have null customers and **zero** revenue (two BPAT 2020 transportation and one CISO 2024 transportation);
- **0** have positive customers or positive revenue;
- by customer class: other 709, transportation 386, industrial 127, commercial 52, residential 47.

Together, original release code + real source values provide **direct mechanistic support** for why all-null category rows may be ETL-preserved category slots. **They do not prove which original respondent values were absent or whether every one of the 1,321 rows is structurally inapplicable.** That last attribution requires original `raw_eia861__sales` source records (or pinned original filings) and a row-level raw-to-processed trace.

An important distinction: the `data_observed=True` column refers to the raw reported/estimated source *record*, not whether every class-specific numerical cell within that record was explicitly supplied as positive electric sales. This inference follows from tagged code that maps O to True *after* reshaping, not a hypothetical interpretation.

## Scientific implications and next test

1. Mark `other` nulls **probable transformed empty category slots**, with explicit unresolved original-file trace; do not fill 709 with zero and do not treat 709 as confirmed positive missing MWh.
2. Keep transportation, industrial, residential and commercial nulls pending source-cell trace for the same reason; their 612 blank values are not **automatically** positive missing energy.
3. The previously published hypothetical missing-5%-MWh coverage bands are **conditional only**, not empirical missing-sales bounds.
4. Annual EIA861 matched-source MWh still do not allocate observed retail demand to counties or hourly BA power system load. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain BLOCKED. `model_training_permitted=false`; 2024–25 demand holdout untouched; C-1 frozen.

**Next decisive execution**: retrieve fixed `raw_eia861__sales` source or original Form 861 sales workbooks, determine *original* class field presence and reported value for each of these 1,321 derived null rows, and report class-stratified verified structural placeholders vs unresolved cases. Do not upgrade E2 from mechanistic plausibility alone.
