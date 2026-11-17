# C-2 E1 — EIA-861 real sales geography coverage pipeline, 2026-11-16

## What was actually completed

Previously verified original PUDL v2026.10.0 BA-utility-state association archive: 1,418 unique year–BA–utility–state keys, including AZPS=146, BPAT=670, CISO=550, SRP=52. Original inner association CSV SHA256 `957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`. The source ZIP available in the project had SHA256 `0e3d5ac5556b155456deb79bbb78be4b707907043764faca29edf1552721385e`, but the *inner CSV digest* is now used because downloadable GitHub Actions archive ZIP metadata can change.

New source-only Python program `src/c2_eia861_sales_geography_coverage.py`, synthetic regression tests `tests/test_c2_eia861_sales_geography_coverage.py` and automatically runnable workflow `.github/workflows/e1-eia861-sales-geography-coverage.yml` were committed. The workflow downloads the old original GitHub artifact via GitHub-token Actions API, checks the original *inner source CSV SHA*, obtains the official fixed PUDL release `s3://pudl.catalyst.coop/v2026.10.0/core_eia861__yearly_sales.parquet` (AWS public no-sign-request), hashes the exact Parquet bytes and computes observed bundled annual retail MWh coverage by year, BA, business model, and source association category.

The workflow accepts an optional *previously verified* source SHA input. **On a first acquisition with no previous SHA, it emits the actual Parquet hash but explicitly marks that acquisition NOT YET PRE-PINNED**; it cannot count as retrospectively preregistered pinned source. On subsequent execution, supply that recorded actual SHA to fail closed on any changed source.

The script rejects missing sales hash, duplicate original composite sales keys, nonfinite/negative sales, excludes `data_observed=false`, `customer_class=total`, and non-bundled service types, and keeps business models distinct. Missing customer counts remain noncomputable rather than imputed as zero. The output is a **conditional share of selected reported observed bundled annual retail MWh** whose utility association has county source records, not the fraction of actual hourly BA demand located in counties. It makes no claim about electric grid stress, customers' precise geography, ALL/NAT climate attribution or future SSP outcomes.

## Execution evidence and blocker

Direct attempt to HEAD the stable S3 Parquet from this execution container failed with `NameResolutionError: Failed to resolve s3.us-west-2.amazonaws.com`. No actual sales values were downloaded here. The GitHub connector returned no accessible workflow run result for initial workflow commit `796e2d5f8b37a6b4cb9f5e57c73a4ab94744e6eb`; this is not proof that Actions is disabled or the workflow definitively failed. **No real MWh/customer coverage estimates exist in this report.**

Independent local re-run of preceding original join package's synthetic unit test suite: 7/7 passed, and original 1,418 real association keys were verified. Newly committed GitHub implementation's CI status is still unverified.

## Research significance and gate

This moves E1 from **count-of-associations** toward a testable **annual energy-sales coverage** criterion without falsely assuming one association equals one customer or megawatt-hour. A high count-based match (notably BPAT) does not establish historical BA load exposure because excluded cross-state county slots remain and actual retail coverage is not known.

Scientific gates remain `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `GEO_LOAD_RELEVANCE=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`, `model_training_permitted=false`. No sealed 2024–2025 demand holdout was used. C-1 frozen.

## Links

- [New source-only sales join](../src/c2_eia861_sales_geography_coverage.py)
- [Seven regression cases](../tests/test_c2_eia861_sales_geography_coverage.py)
- [Download and analysis Actions workflow](../.github/workflows/e1-eia861-sales-geography-coverage.yml)
- [PUDL versioned storage documentation](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html)
- [PUDL official sales schema](https://data.catalyst.coop/preview/pudl/core_eia861__yearly_sales)
