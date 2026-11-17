# C-2 E1 — Annual EIA861 sales acquisition: verified local tests and resilient fixed-release retrieval (2026-11-16)

**Real annual retail sales MWh not yet retrieved. No empirical MWh coverage percentage is claimed.**

## Source verification performed locally
- Executed the prior independent seven-test `c2_eia861_sales_join.py` suite against synthetic sales fixtures: **7/7 tests passed**; these do not replace new GitHub CI.
- Parsed the actual archived PUDL v2026.10.0 association CSV `EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv` from existing artifact 14144934238. Its inner SHA256 is `957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`.
- Verified **1,418 distinct year-BA-utility-state keys**, source BA counts AZPS 146, BPAT 670, CISO 550, SRP 52; and **28** nonexclusive year-utility-state combinations linked to multiple study BAs.

## Current actionable acquisition improvement
GitHub workflow `.github/workflows/e1-eia861-sales-geography-coverage.yml` commit `c55bc0d165a41e24d653823c66a8314460d26260` now:
1. Attempts anonymous AWS CLI download of `s3://pudl.catalyst.coop/v2026.10.0/core_eia861__yearly_sales.parquet`, matching PUDL official [versioned storage documentation](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html).
2. If AWS CLI fails, retries the **same immutable object** via path-style `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.10.0/core_eia861__yearly_sales.parquet` (avoids dotted-bucket virtual-host TLS problem).
3. Saves `sales_acquisition.log`, Parquet SHA256, the first-acquisition not-pre-pinned marker or provided pinned SHA comparison, and a downloadable failure diagnostic if unsuccessful.

PUDL [annual sales table schema](https://data.catalyst.coop/preview/pudl/core_eia861__yearly_sales) specifies utility, state, report date, BA code, customer_class, business_model and service_type primary key; sales_mwh, customers, data_observed and data_maturity columns. It defines bundled versus energy-only versus delivery-only.

The prior local direct public S3 request failed on DNS; the latest GitHub connector queries have **not exposed an independently verified completed workflow**. Neither the backup strategy nor code existence means downloaded data or actual BA-year MWh results have been obtained.

## Scientific status
Source association counts cannot be interpreted as load-weighted geography; the requested actual observed annual retail sales numerator/denominator are still unavailable. Further BA weather exposure validation and E2 model training remain blocked. No 2024–2025 test-period *demand* data were used to fit or tune models; C-1 remains frozen.
