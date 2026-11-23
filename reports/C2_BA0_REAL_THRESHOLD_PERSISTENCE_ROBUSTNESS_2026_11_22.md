# C-2 BA-0 — Threshold robustness and 3-day persistence sensitivity (2026-11-22)

**Executed on real source-matched data.** Full standalone reproducibility package: `C2_BA0_Threshold_3Day_Robustness_2026_11_22.zip`, SHA256 `b1d54ccb2da82b7148958125f4e5c646ecbd40e47f66f8d523461266fbc80096`. The user package includes source-SHA-pinned script, five passing contract tests, CSVs, report, plot and file-hash inventory. It does **not** include a license to treat exploratory BA spatial masks as approved operational geography.

## Design

- Input: 10,416 authentic exact UTC-hour EIA-930 × ARCO ERA5 paired rows, input SHA256 `e754b35f2c6aaeb80b2a932cc9885382d3a1a93ae0d59cc27077810e65bbeb5c`.
- 14 complete BA×months (31 complete UTC days each); AZPS 2023 omitted because of strict source QA failure; 2025 data already descriptively explored (not pristine blind holdout).
- Compare HIFLD 2018 candidate area proxy A with TIGER 2024 county candidate B using *the same* ERA5 2m temperature source and identical UTC stamps.
- Enumerate 8 illustrative thresholds: 28, 30, 32, 34, 35, 36, 38, 40°C (112 BA-month-threshold rows).
- Paired circular moving day-block bootstrap: 1-day vs 3 consecutive UTC-day blocks, truncate to the original 31-day month. 2,000 replications, fixed seed 20261122; conditional percentiles only. 28 BA-month-target persistence comparisons (mean temperature delta, >35°C hourly count delta).

## Actual results

| BA × July | A >35°C | B >35°C | Difference B−A hours | 1-day 95% bounds | 3-day 95% bounds |
|---|---:|---:|---:|---:|---:|
| CISO 2023-07 | 38 | 31 | −7 | [−13,−2] | [−13,−2] |
| SRP 2023-07 | 472 | 373 | −99 | [−112,−86] | [−114,−85] |
| AZPS 2025-07 | 135 | 79 | −56 | [−74,−39] | [−77,−35] |
| SRP 2025-07 | 326 | 222 | −104 | [−118,−92] | [−123,−86] |

At all eight tested thresholds from 28 to 40°C, B−A exceeds-zero counts are **negative** for SRP July 2023, SRP July 2025 and AZPS July 2025 (the negative gap may become small at 38–40°C); CISO July 2023 is negative up to 36°C, then zero at 38 and 40°C. BPAT July 2023/2025 has zero >35°C exceedances under both masks. These demonstrate *heterogeneous geographic support sensitivity*, not universal increased risk.

When comparing mean candidate B−A temperatures, the 3-day bootstrap has **wider 95% conditional intervals for all 14 BA×month cohorts** than 1-day sampling, emphasizing temporal-persistence sensitivity. Moving-block resampling does not estimate year-to-year or boundary uncertainty, and these intervals must not be used as climate projection confidence intervals.

## Interpretive locks and next gate

Neither proxy is certified BA operational or load-weighted geography. 35°C is illustrative, not a calibrated grid stress criterion. No predictive model was fitted, no causal warming attribution was performed, and no PyPSA adequacy metric or CMIP6 SSP forecast has been produced. Current data support a source-conditional sensitivity finding, **not** a full generalizable publication claim. Future work: verified BA footprint, source-pinned annual ERA5 weather coverage, predeclared non-leaky multiyear evaluation, and independent counterfactual design before causal attribution. C-1 remains frozen.
