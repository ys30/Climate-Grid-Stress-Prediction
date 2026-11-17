# C2 E1: Annual retail-sales coverage by BA–utility–state (2026-11-16)

**Status: source association data independently checked; a reproducible sales join has passed seven synthetic tests; real PUDL sales file has not yet been retrieved. No actual MWh coverage percentage is claimed. C-1 frozen, E2 blocked.**

## Actual source verified
Immutable existing PUDL v2026.10 original utility–BA–state archive (GitHub Actions artifact 14144934238, ZIP SHA256 `0e3d5ac5556b155456deb79bbb78be4b707907043764faca29edf1552721385e`). Its `EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv` contains 1,418 distinct year–BA–utility ID–state records, 2020–2025; the program verifies the original archive SHA before joining.

## Official external sales source
The official PUDL `core_eia861__yearly_sales` table has primary key `utility_id_eia, state, report_date, balancing_authority_code_eia, customer_class, business_model, service_type`; also includes `data_observed`, `sales_mwh`, and `customers`. See:
- https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html
- https://data.catalyst.coop/preview/pudl/core_eia861__yearly_sales

Pin the *versioned* `s3://pudl.catalyst.coop/v2026.10.0/core_eia861__yearly_sales.parquet`, record its SHA256 and use alongside the original bridge. Do NOT substitute changing nightly data without independent provenance. This external sales Parquet could not be downloaded in the execution environment (outbound network unavailable).

## Reproducible implementation delivered in this conversation

Artifact `C2_E1_EIA861_SALES_GEO_JOIN_SOURCE_ONLY_20261116.zip` (ZIP SHA256 `76b51508e19ec83af8f9d9b0cfb0cb40bc9a4f4d7599be838198acf5b6daa9ec`) contains:
- `c2_eia861_sales_join.py`: verifies 1,418 original association records and source archive SHA; requires pinned sales file SHA; maps on year–BA–utility ID–state; rejects duplicate PUDL sales composite keys, invalid/nonfinite/negative values; excludes imputed/unobserved records and all customer-class totals; restricts initial denominator to reported `bundled` sales and stratifies by business_model; retains geography-matched, county-unmatched, and absent-association categories; does not turn missing customers into zero; writes two CSV reports and JSON audit.
- `test_c2_eia861_sales_join.py`: seven passing **local synthetic** unit tests. Actual pinned original bridge successfully parsed and passed 1,418-row integrity check.
- `README.md`: exact reproduction command and accounting restrictions.

**Scientific limitation:** the resulting future measure (when sales data obtained) will be *percent of selected observed bundled retail MWh attached to a utility/BA/state association with some available county source*, **not** the proportion of hourly BA electric demand that has been spatially resolved. A utility county location may be cross-BA or nonexclusive. Distinct customer class/business model semantics require validation before any full-BA retail sum or spatial customer allocation. A/E/B/C weather exposure geometries remain unapproved.

## Next empirical acceptance evidence
1. Download and SHA-pin the actual PUDL v2026.10 sales Parquet.
2. Report the year/BA/business-model MWh numerator and denominator together with excluded/missing/source-absent rows; do not present a percentage alone.
3. Audit service type and class overlap against EIA Form 861 data definitions; independently test BA-to-utility-to-county electric-load relevance.
4. Only after separately clearing scientific gates consider E2 models. `model_training_permitted=false` now.
