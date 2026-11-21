# C-2 E1: independent California QFER county/utility source discovery and admissibility checks (2026-11-20)

**New external official-source discovery only. No derived county allocation has yet been confirmed. C-1 frozen.**

## Direct primary-source links discovered

The [California Energy Commission (CEC) official energy consumption data files](https://www.energy.ca.gov/files/energy-consumption-data-files) publish separate annual electric-consumption workbooks:
- [AGG_CONSUMPTION_ELEC_COUNTY_TBL_ada.xlsx](https://www.energy.ca.gov/filebrowser/download/8144?fid=8144), official county aggregate annual workbook.
- [AGG_CONSUMPTION_ELEC_UTILITY_TBL_ada.xlsx](https://www.energy.ca.gov/filebrowser/download/8168?fid=8168), official utility aggregate annual workbook.

The [CEC Electricity Consumption methodology](https://www.energy.ca.gov/data-reports/energy-almanac/california-electricity-data/california-energy-consumption-dashboards-0) documents that the QFER 1306A Schedule 1 originates from reporting **distribution utilities**, and data are available by county, agency, sector and annual/monthly time. The CEC explicitly defines *consumption* as **retail sales + non-retail consumption + self-generation**, a wider estimand than EIA-861 selected bundled retail sales. The CEC says its dashboard was updated **January 27, 2026**, including observations **through 2024**. Thus even a source-backed 2020–2024 CEC geographic series cannot be silently carried forward to 2025.

EIA's [official geographic electricity-data FAQ](https://www.eia.gov/tools/faqs/faq.php?id=448&t=1) clarifies that EIA-861 includes utility sales and lists **counties with utility distribution equipment**, but these are *service territory indicator counties*, not unique load-by-county sales; multiple utilities can share counties.

## Necessary no-leakage distinctions

1. **Annual EIA861 sales vs CEC consumption:** different reporting scope and self-generation treatment; never compare unadjusted gross totals as identical.
2. **CEC county aggregate vs CEC utility aggregate:** a county total \\(C_c\\) and a utility total \\(U_u\\) do not identify each joint county×utility cell \\(x_{uc}\\); many feasible nonnegative matrices share the same margins, even if their totals agree. A county-file plus utility-file alone cannot prove a joint observation. First inspect workbook sheet headers and any available agency-by-county joint keys.
3. **CEC utility reporting area vs CISO electricity BA:** neither agency nor county affiliation automatically establishes CISO's time-varying EIA-930 balancing-area footprint or eligible hourly demand-weighted weather exposure.
4. **CEC 2024 vs 2025:** 2024–25 EIA930 hourly demand model test remains untouched and cannot be tuned using CEC evidence to select weather proxy definitions.
5. **Arizona and Pacific Northwest:** California QFER cannot certify AZPS, SRP or BPAT geography.

## Actual implementation and next acceptance

New source-only audit `scripts/c2_cec_qfer_external_county_utility_schema_probe.py` uses standard-library read-only XLSX ZIP/XML inspection, preserves original downloaded workbooks' first-observed SHA-256 and sheet-layout previews, but NEVER assumes an annual county×utility MWh allocation. Synthetic source-fixture regression:
`tests/test_c2_cec_qfer_external_county_utility_schema_probe.py`.
GitHub workflow `.github/workflows/c2-cec-qfer-external-schema.yml` downloads the two official original workbooks and preserves **only JSON schema/hashes** in its artifact (not redistributing source Excel files). First run:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44872398200
**was queued when written**. Its success and the actual workbook content require inspection before asserting any empirical field layout or joint observation.

A direct local HTTP retrieval of the published CEC XLSX link failed during DNS resolution, *prior* to any workbook response, so this report claims only externally verified web metadata and an executable source-inventory workflow.

## Scientific implications

Independently completed PUDL v2026.10.0 retail sales and conditional utility-county bound analyses already established **924,201,242 MWh** selected actual 2020–23 annual retail sales, **757,691,947 MWh** multi-county source-ambiguous, and **20,217,011 MWh** not linked to source counties. No reason exists to re-download that already-verified PUDL as a prerequisite here.

**GEO_LOAD_RELEVANCE remains BLOCKED** until source-specific reported county or metered load allocations can be separately authenticated. E2 GAM/XGBoost/weather attribution and SSP–PyPSA outcomes remain uncomputed; `model_training_permitted=false`. C-1 frozen.
