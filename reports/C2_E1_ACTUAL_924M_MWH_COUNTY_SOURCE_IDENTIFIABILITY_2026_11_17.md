# C-2 E1 — Actual observed retail MWh by county-source identifiability, 2020–2023 (2026-11-17)

## Research question

What fraction of **actual observed annual electricity sales MWh** in the four-BA historical training/validation period can be associated with **one**, **multiple**, or **no** reported utility service counties in the original PUDL EIA-861 data? This measures *geographic identifiability of utility reporting sources*, **not actual load allocations or validation of BA operating polygons**.

### Actual immutable inputs and run

- Original source: PUDL **v2026.10.0** `core_eia861__yearly_sales.parquet`, SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`.
- Version-pinned utility × BA × year × state original FIPS evidence: 933 rows from previously successful [run 44228454642](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44228454642), artifact 14393473675, source underlying `core_eia861__yearly_service_territory.parquet` SHA256 `3d6c4cc54bd856e678fa0b3eb162e2c8867a3fbe64dfae8f862f0dd82cca0605`.
- Source filtering matches earlier published sales study exactly: `data_observed=true`, `service_type=bundled`, known non-total customer classes, non-null nonnegative `sales_mwh`; preserve `business_model` in detail. Every original sales record is linked using the exact year–BA–utility EIA ID–state key. Zero, one, multiple county FIPS and missing source link are mutually exclusive for each selected sales record; nonexclusive BA source is a separately recorded *overlapping flag*.
- New script `src/c2_e1_real_sales_county_identifiability.py`; tests `tests/test_c2_e1_real_sales_county_identifiability.py`; workflow `.github/workflows/e1-observed-sales-county-identifiability.yml`.
- Real [GitHub Actions run 44242371793](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44242371793) **SUCCESS**, artifact **14400412064**, downloaded and checked independently.
- **All 16 historical BA–year actual MWh grand totals independently reconciled** with the earlier tagged-source EIA861 sales coverage artifact **14310951946**. No sales imputed.

## New observed annual retail MWh result (sum 2020–2023, per BA)

| BA | Total selected observed bundled MWh | One reported utility county MWh (% of BA) | Multi-county utility MWh (% of BA) | No county FIPS MWh (% of BA) |
|---|---:|---:|---:|---:|
| AZPS | 129,057,618 | 4,840,693 (**3.75080%**) | 120,464,912 (**93.34196%**) | 3,752,013 (**2.90724%**) |
| BPAT | 207,663,786 | 83,728,317 (**40.31917%**) | 123,932,777 (**59.67953%**) | 2,692 (**0.00130%**) |
| CISO | 463,195,807 | 57,723,274 (**12.46196%**) | 389,552,906 (**84.10113%**) | 15,919,627 (**3.43691%**) |
| SRP | 124,284,031 | 0 (**0.00000%**) | 123,741,352 (**99.56336%**) | 542,679 (**0.43664%**) |
| **All four BA** | **924,201,242** | **146,292,284 (15.82905%)** | **757,691,947 (81.98344%)** | **20,217,011 (2.18751%)** |

All 16 source BA–years had **zero observed MWh without a source utility–BA association**. Nonexclusive utility–BA source MWh, which is a separate intersecting risk category, totals **3,934,759 MWh (0.42575%)** across all four BAs (AZPS 3,379,675; BPAT 0; CISO 12,405; SRP 542,679). These values represent **source reporting associations**, not double counted electric demand, and the nonexclusive category must NOT be added to mutually exclusive county categories.

### Scientific consequence for geographic load weights

A successful original utility–county source linkage is not a utility–county **MWh fraction**. **81.983%** of selected four-BA annual retail MWh belong to reporting utilities with **multiple** county source records, with no actual MWh by county in the joined EIA861 tables. **2.188%** have no county FIPS at all. The remaining **15.829%** have just one county reported in that source, but that alone is not an independent confirmation of customer electricity-location, operating BA polygon, or hourly BA demand allocation.

This reveals why earlier county-*matched*-sales shares (AZPS 97.09%, BPAT 99.999%, CISO 96.56%, SRP 99.56%) must not be represented as spatial demand-weight coverage. In particular SRP's ~99.56% county-source match does **not** yield identifiable county MWh allocation because **all** county-linked sales lie in multi-county source associations.

Official EIA-861 scope: annual retail sales/revenue/customers reported by state, sector, utility and BA; service territory lists county FIPS, **without county-allocated sales MWh**. References: https://www.eia.gov/electricity/data/eia861/ and https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html.

## Next decisive checks

1. Check whether any independently acquired county-specific metered electricity data or supported service-territory allocation can be **validated against the original annual actual BA–utility–state MWh**; reject simple equal-county weighting as a factual observation.
2. Obtain source-vintage-approved historical BA operating territory with topology and code crosswalk (not BA county unions).
3. Distinguish *source county association* from actual hourly BA *demand*; do not allow model training until geography and holdout protocols pass separately.

Scientific status: `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `GEO_LOAD_RELEVANCE=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`, `model_training_permitted=false`. C-1 frozen; sealed 2024–2025 EIA-930 hourly demand unused.
