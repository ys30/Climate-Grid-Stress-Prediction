# C-2 progress and scientific milestone audit — 2026-11-26

## Executive status

The C-2 historical attribution + future climate/grid prediction research is **not yet ready for final model inference or manuscript results**. Real historical source acquisition has advanced significantly; BA operational geography, FERC independent validation and scenario-model admission remain material blockers. The following statuses deliberately distinguish original data and real-source checks from scripts and tests.

## Evidence-based historical progress

- Actual archive of 2020–25 72 months of EIA930+ERA5 matching across AZPS/BPAT/CISO/SRP: 210,432 BA × UTC-hour record candidates; 210,172 observed demand matches and 260 missing, 70 anomaly candidates (as reported in the prior source audit).
- BPAT EIA-930 bulk-vintage demand was re-extracted: 52,608 unique UTC-start hours 2020–25, 0 missing BPAT hours; years 8,784/8,760/8,760/8,760/8,784/8,760. Actual derived CSV SHA-256 `65e51c15227eb9aae84ce65b35038ea458fd8e2fdb6c9608211268e8291761bc`. This does **not** resolve cross-vintage EIA-930 differences.
- BPA historical FERC714 respondent ID 122, EIA numeric 1738, PUDL respondent ID 21, XBRL C002357 backed by pinned historic FERC respondent CSV (Git blob `2472dfbd531857969cfaf16e6dbc2d0fba6552bd`) and PUDL cross-era glue (Git blob `3eb0291e51502df9a5fca38e9f3ac4ebf3526ad7`). The respondent 21 current fixed-version core Parquet row has not yet been checked, so this chain is **historical source-supported identity**, not independently certified current-release hourly coverage.
- The published fixed `v2026.10.0` PUDL core FERC714 hourly Parquet extraction workflow and actual per-row export have been committed. **No authenticated PUDL respondent 21 actual hourly CSV artifact or successful CI run was obtained as of this report**.
- Geographic county-union and EIA861 annual respondent/utility proxy checks are **not** approved time-varying operational BA polygons or hourly county consumption weights.

## This turn's direct correctness improvement

In `scripts/c2_bpat_ferc714_21_vs_original_eia930_hourly.py` the original code rejected duplicate FERC hours only within each `(report_year, datetime_utc)` pair, although PUDL says the natural core-hourly primary key is `(respondent_id_ferc714, datetime_utc)`. This permitted the same physical hour in different reporting-year cohorts and could double-count it. The revised code now rejects **any duplicate UTC timestamp** across the full 2020–25 FERC respondent sample. It also produces explicit matched/expected fractions for -1, 0, +1h sensitivity shifts and an `all_expected_hours_matched` admission flag, keeping a year with only 1,000 pairs from being described as a complete 8,760-hour comparison.

Two new synthetic tests were committed for cross-report-year duplicate hour and incomplete overlap. They are test **definitions**; this turn has not independently observed a GitHub Actions run passing after the change.

## Research objective A: retrospective decomposition

The planned decomposition separates interannual weather fluctuations, longer-term climate changes, their interaction and extremes, with BA/year counterfactuals and defensible load/generation mapping. Infrastructure and source consistency are partially assembled, but actual attribution estimates are **not scientifically approved**: no verified historical operational BA geography, source-vintage harmonization or externally validated climate trend counterfactuals. Previously inspected 2025 cannot be presented as untouched blind holdout.

## Research objective B: forward prediction

CMIP6/SSP scenario catalog and 2030/2040/2050 multi-BA PyPSA stress experiments are still the design stage. SSP126/245/370/585, extreme heat and low-wind combinations can be specified; **do not claim an ensemble quantity, trained surrogate or approved forecasts until source inventory and scenario runs are verified**. No full real scenario-run result is authenticated in this turn.

## Priority order

**P0** Get and hash-validate actual fixed PUDL v2026.10.0 respondent 21 hourly core Parquet-derived CSV, with year-of-report vs UTC-year diagnostics.

**P1** Run cross-source BPAT comparison on paired observations, with explicit lead/lag convention and annual coverage checks; investigate whether FERC planning-area demand and EIA930 BPAT BA operational load represent equivalent scopes. Distinguish source-vintage effects and missing source rows.

**P2** Acquire/time-index historical BA operational territory and scientifically defensible geographic allocation or present a non-spatial historical model that does not require unapproved weights.

**P3** Only after source QA, fit pre-registered historical weather/climate effects and uncertainty intervals, then extend to validated CMIP6 SSP/PyPSA stress scenarios.

C-1 remains frozen. No FERC hourly measured MAE/Bias, no climate causal effect size and no future grid stress forecast is asserted.
