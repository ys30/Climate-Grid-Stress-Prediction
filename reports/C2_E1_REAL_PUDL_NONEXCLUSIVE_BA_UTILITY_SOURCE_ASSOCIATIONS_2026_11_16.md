# C-2 E1 source association nonexclusivity: verified real 2020–2025 PUDL metadata (2026-11-16)

## Independently verified original source
Original GitHub Actions artifact `14144934238` (PUDL v2026.10.0 utility/BA/state association), inner `EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv` SHA-256 `957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`.

A separate original-CSV reader verified:
- **1,418** BA–utility–state–year source associations;
- **1,382** unique (year, utility ID, state) combinations;
- **28** distinct (year, utility ID, state) combinations connected to **multiple** target BAs;
- **64** total BA-association source records covered by those 28 combinations (36 links in excess of one exclusive link);
- by BA: AZPS **28**, SRP **28**, CISO **8**, BPAT **0**;
- **all 64 nonexclusive BA-association records have zero matched county-source entries** in the actual archived bridge. Thus they sit *within*, not outside, the 439 unmatched association records reported in the prior geographic QA; do **not** add 64 to 439.

BA-year nonexclusive association counts from actual original CSV:
| BA | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|---:|
| AZPS | 5 | 4 | 4 | 4 | 5 | 6 |
| SRP | 5 | 4 | 4 | 4 | 5 | 6 |
| CISO | 1 | 1 | 2 | 2 | 1 | 1 |
| BPAT | 0 | 0 | 0 | 0 | 0 | 0 |

## New program and regression change
`src/c2_eia861_sales_geography_coverage.py` now computes, from original bridge keys, whether a given (year, utility, state) is linked to multiple BAs. It labels these source association rows separately from exclusive county-matched rows when processing future actual EIA-861 observed annual bundled sales. Its annual/business-model report now also emits nonexclusive association MWh and nonexclusive-but-county-matched MWh separately. The `tests/test_c2_eia861_sales_geography_coverage.py` test suite gained a synthetic scenario ensuring sales in a nonexclusive county-matched source category are not silently credited to the strict/exclusive numerator. This is a conservative geography-source interpretability choice, not proof that BA-labelled retail sales records themselves are duplicates.

Code commit `07671fcab8b80da8ecaa874a620c5f068a9464c4`; new test commit `dc751fc320cdf9108c7c62c6aa8ae020263fb963`. GitHub Actions pass not yet independently confirmed.

## What is still not measured

This audit **does not contain real PUDL `core_eia861__yearly_sales.parquet`**: current execution container could not connect to the public PUDL S3 endpoint. Consequently no MWh-, customer-, or hourly BA-demand-weighted geography coverage result can be reported. The current public PUDL documentation identifies the primary key `utility_id_eia, state, report_date, balancing_authority_code_eia, customer_class, business_model, service_type`; it distinguishes bundled service from energy-only and delivery-only records. See [PUDL data dictionary](https://docs.catalyst.coop/pudl/en/latest/data_dictionaries/pudl_db.html) and [versioned storage](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html).

Archived independent audit package `C2_E1_NONEXCLUSIVE_UTILITY_ASSOCIATIONS_20261116.zip`, SHA256 `76e4ef1709750d44f25ae0024d8f5f4fedd7022f95a78e80b3a5d8a0324b6faa`, includes year/BA CSV, all nonexclusive source keys, JSON, methodology and reproduction script.

2024–2025 *demand* test was not used. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE` and `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain blocked, `model_training_permitted=false`. C-1 frozen.
