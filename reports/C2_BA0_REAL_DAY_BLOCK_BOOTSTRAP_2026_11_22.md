# C-2 BA-0: authentic within-month UTC-day block-bootstrap sensitivity (2026-11-22)

**Status:** completed exploratory, source-clock validated, **not** model/geography approved. Input is the authenticated 10,416-row EIA-930 × ERA5 four-month UTC-paired data, CSV SHA-256 `e754b35f2c6aaeb80b2a932cc9885382d3a1a93ae0d59cc27077810e65bbeb5c`. Four months are Jan/Jul 2023 and Jan/Jul 2025; all four BAs except strict-source-failed AZPS 2023.

## Executed method

For each of 14 BA×months (744 hours = 31 complete UTC days), compute the paired hourly difference in actual ARCO ERA5 t2m area proxy: 2024 TIGER/Census candidate B minus HIFLD 2018 candidate A. Evaluate hourly exceedance of illustrative 30°C and 35°C and A-only / B-only event discrepancies. Resample **paired 24-hour UTC day blocks**, 31 draws with replacement, 2,000 times per month, fixed seed 20261122. Report 2.5 and 97.5 percentile conditional day-resampling bounds. This handles within-day dependence, but does not quantify full climate-year, geographic-boundary or multiday weather persistence uncertainty.

| BA × month | A >35°C hours | B >35°C hours | B−A hours | Conditional day-block 95% bounds |
|---|---:|---:|---:|---:|
| CISO 2023-07 | 38 | 31 | −7 | [−13,−2] |
| SRP 2023-07 | 472 | 373 | −99 | [−113,−86] |
| AZPS 2025-07 | 135 | 79 | −56 | [−74,−39] |
| SRP 2025-07 | 326 | 222 | −104 | [−118,−91] |

Mean temperature B−A examples and conditional day-block bounds (°C): AZPS 2025-01 = −2.060 [−2.230,−1.905]; SRP 2023-07 = −1.807 [−1.896,−1.717]; CISO 2023-07 = −0.290 [−0.351,−0.226]; BPAT 2023-07 = −0.195 [−0.237,−0.152].

Full **14 BA×month** CSV reports 30/35°C event counts, both/A-only/B-only/neither confusion counts, Jaccard where defined, mean B−A temperature and day-block bounds. Data calculations were executed locally on source hash-pinned input; **4 deterministic actual-data contract tests passed**.

## Reproducibility and limitations

The user-delivered archive `C2_BA0_DayBlockBootstrap_GeographicSensitivity_2026_11_22.zip` (SHA-256 `a345810743cace71f56ca4bcf73c4ef0613ca73adf01158d4f6707ae2effc5fc`) contains the standalone Python script, 14-row output CSV, SHA manifest, report and four tests. Script verifies input SHA, source flags and exact BA-hour UTC completeness and refuses to overwrite outputs. No original data or protected keys are published to the repo.

**Interpretation locks:** Both weather proxy masks are *unapproved* for actual BA demand-weighted operating geography. Bounds describe conditional within-month day resampling; they are **not** climate projection confidence intervals, independent multiyear inferential samples, significance tests or evidence of grid adequacy. 35°C is an arbitrary demonstration threshold, not calibrated operational stress. 2025 weather/demand was already descriptively viewed and is **not pristine blind holdout**. No predictive model, causal forcing attribution, or PyPSA/SSP simulation has been conducted. AZPS 2023 remains strictly excluded. C-1 is frozen.

Next priority: actual operational BA geography and load weighting; full-year historical hourly ERA5 acquisition; preregistered leakage-aware out-of-year forecast evaluation after genuine source gates.
