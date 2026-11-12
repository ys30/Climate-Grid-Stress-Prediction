# C-2 E0 2020–2025 official EIA-930 hourly demand coverage — first complete annual audit

## Verified source-audit execution (2026-11-12)
- Original six-year matrix succeeded: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43293803414
- Six parallel year-specific jobs, each using both original EIA official Jan–Jun / Jul–Dec BALANCE files, preserving raw reported Demand (MW), converting hour-ending UTC to start-hour UTC, storing input SHA256/coverage report as GitHub Actions artifacts.
- These results **measure reporting availability, not EIA demand truth, weather attribution, climate change causation or actual outages**.

## Valid hourly source records by year and BA
| Year | Expected hours / BA | AZPS | BPAT | CISO | SRP |
|---|---:|---:|---:|---:|---:|
| 2020 | 8784 | 8753 | 8776 | 8773 | 8729 |
| 2021 | 8760 | 8753 | 8752 | 8747 | 8728 |
| 2022 | 8760 | 8753 | 8752 | 8749 | 8752 |
| 2023 | 8760 | 8751 | 8752 | 8750 | 8753 |
| 2024 | 8784 | 8777 | 8776 | 8728 | 8729 |
| 2025 | 8760 | 8753 | 8752 | 8704 | 8750 |

All 24 BA-year valid-hour fractions exceed the preregistered 99% annual coverage threshold, but **none is 100%**. Every BA-year has 7 or 8 missing timestamp keys under the present source normalization; verify their locations and whether additional adjacent-vintage files resolve them before deciding gap policy.

## Known original missing/invalid demand source entries (not missing timestamps)
- 2020: AZPS 24; CISO 3; SRP 48.
- 2021: CISO 5; SRP 25.
- 2022: CISO 3; SRP 1.
- 2023: AZPS 2; CISO 2.
- 2024: CISO 48; SRP 48.
- 2025: CISO 48; SRP 3.
- Other BA-year blanks zero per CI. Duplicate BA-hour keys: zero across all 24 BA-year audits.

**Extremes gate:** A 2023 SRP reported raw maximum of 70,313 MW appeared in the source audit; this is extraordinarily large for that BA, and cannot be trusted as a genuine peak without checking the exact timestamp, source record, units, revisions, and nearby hourly values. Do not train on the unreviewed extreme or report it as physical observed peak.

## Next source-quality gates (required before model fitting)
1. Merge all six independent artifact CSVs, then apply train 2020–22 / validate 2023 / test 2024–25 gate to the aggregate, not one year at a time. Workflow commit `9f831be71f9e7c5b9773183e936cca89ca90e155` adds the combined gate but its final CI result is pending verification.
2. Emit exact timestamps and durations for missing/blank hours, and a robust, BA-specific candidate-anomaly table. Never clip source extremes silently.
3. Test whether 7/8 annual boundary missing keys arise from source file partition selection (prior year/current year/next year). Check exact UTC interval keys and original archive revisions.
4. Build an actual source-linked, hourly, leakage-free dataset for model training. Annual aggregate coverage alone does not admit a heatwave event or justify imputation.
5. ERA5 BA-area exposure construction and time-independent calibration/validation; do not reuse C-1 illustrative four point ERA5 temperatures as representative regional exposures.

## Limits
Annual coverage >99% does not imply a publishable prediction model; this report only settles the broad source feasibility question. Model skill, weather response and CMIP6 SSP forecasts are not yet estimated.
