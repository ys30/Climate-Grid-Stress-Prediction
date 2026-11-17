# C-2 E1 — Missing-sales BA/year handling and actual PUDL data acquisition status (2026-11-16)

## Confirmed current blocker

Official [PUDL v2026.10.0 storage instructions](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html) support the exact frozen source URI `s3://pudl.catalyst.coop/v2026.10.0/core_eia861__yearly_sales.parquet`. The [PUDL annual sales dictionary](https://data.catalyst.coop/preview/pudl/core_eia861__yearly_sales) confirms primary key (utility, state, report_date, BA, customer_class, business_model, service_type); `sales_mwh`, `customers` and `data_observed` are available. A *direct* attempted request to the path-style S3 HTTPS endpoint `s3.us-west-2.amazonaws.com` from this local container failed at DNS resolution, before a status response. Consequently actual sales bytes and any resulting observed MWh or customer coverage figures **remain unavailable**.

The GitHub connector also returned no accessible workflow run object for relevant latest commits; the presence of a source workflow file does NOT establish that it has run. Review/run at [EIA-861 annual sales source workflow](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/workflows/e1-eia861-sales-geography-coverage.yml). Its source acquisition should produce an original Parquet SHA256, a detailed selected observed bundled sales CSV, 24 BA–year coverage/status summary and QA provenance. First downloaded hash is a *newly observed source digest*, not an independently preapproved historical pin.

## Specific accounting correctness bug identified and fixed

The previous annual sales join silently omitted a BA-year whenever **no observed, bundled, non-total sales** were selected. Missing BA-year results must not be interpreted as zero annual sales or complete study-area coverage.

Commits:
- `a01836116966bcbde9eaa98f8cd9cca1569ba1c5`: explicit missing BA-year observations in the annual output for the full expected `4 BAs × 6 years = 24` grid. Missing strata now have `business_model=NOT_REPORTED` and null MWh, null customer counts and null coverage ratios (never fabricated 0), with training admission false.
- `6fa311cc457e185b7c9adbca8e82dc7d32c6da05`: update existing seven regression tests and add a synthetic test that exactly **23 of 24 BA-years are missing** when only one BA-year has sales; nulls and fail-closed flags checked. **Tests committed; most recent GitHub CI execution not verified.**
- `a3cf7fc1212f70c783fa29577b401e9eb545f9ea`: source manifest records expected vs observed/absent BA-years, explicitly sets `missing_BA_year_is_zero_sales=false`, and separates output row count from the expected 24 BA-year slots.

## Scientific interpretation and research status

Even if real retail sales coverage is obtained in a future workflow artifact, it measures only source association coverage for selected *reported bundled retail electricity sales*, **not** county-level spatial load weights and not hourly BA balancing demand. Nonexclusive utility/BA geography remains separately reported, and associations with missing county source cannot be treated as geographically solved. Existing 1,418 source utility–BA–state associations are original observed crosswalk metadata, not MWh totals.

**NO claimed actual MWh coverage values**, no E2 GAM/XGBoost training, no ALL/NAT attribution or SSP/PyPSA simulation. `model_training_permitted=false`, C-1 frozen. 2024–2025 sealed demand holdout not used to tune or fit model.
