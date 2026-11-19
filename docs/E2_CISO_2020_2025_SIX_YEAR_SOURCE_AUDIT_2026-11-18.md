# C-2 E2 CISO 2020–2025: independent real-source audit checkpoint

Evidence snapshot from corrected [Wave 1 run 44449661959](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44449661959), independently reopened ZIPs for CISO 2020–2023, combined with previously SHA-audited CISO 2024 and 2025 artifacts.

**Scope:** EIA-930 BA CISO actual reported demand (`type=D`), calendar-year UTC interval-start. This is neither ERA5-joined data nor climate-impact attribution. Official null demand values are missing, never 0 or interpolated.

| Year | Expected UTC hours | Valid demand hours | Missing UTC timestamps | Source null demand rows | Effective coverage | Mean valid demand MW | Peak MW |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 8784 | 8781 | 0 | 3 | 99.965847% | 24814.17 | 46643 |
| 2021 | 8760 | 8754 | 1 | 5 | 99.931507% | 25019.65 | 43615 |
| 2022 | 8760 | 8757 | 0 | 3 | 99.965753% | 25533.96 | 51104 |
| 2023 | 8760 | 8758 | 0 | 2 | 99.977169% | 24907.22 | 44007 |
| 2024 | 8784 | 8784 | 0 | 0 | 100% | 25504.36 | 47571 |
| 2025 | 8760 | 8760 | 0 | 0 | 100% | 25573.49 | 43860 |

All six annual source gates pass the preregistered >=98% coverage threshold. **Missing rows still require explicit treatment in any fitted model or pairwise lag evaluation**; this approval does not authorize arbitrary filling or assuming complete hourly weather joins.

## SHA-256 verification of corrected-wave raw and converted artifacts

| CISO year | Raw HE CSV SHA-256 | UTC-start CSV SHA-256 |
|---|---|---|
| 2020 | `62f2ebecb7c22b1ea7a6daf993afbaebfe13bc9950df210de81261ec6cc63b29` | `197369eba96ac5e047932f20fce54f25a8dcaea88f8d68b9a8d1ea63c66059c9` |
| 2021 | `aea75bb41b31cf4bc66af13fdaeae17dc6f64e77c43c6077e90a442d6e01469c` | `f7a9a563f91c01d583a98c6e632d3042b077d5a25eee18f62d6e2f535c1b6151` |
| 2022 | `ba45de0f7018a75aaa92a3e7e1eb16e577d5a2c7fb47971429a090dd124360ab` | `d5ae41cc5ed3d16ef66bfed297ae892d7ef09b8d406973ce0adf196867f9cbf2` |
| 2023 | `1bc4b7fb4debfd0c2c9905380345f8616d64491735b733f95ffdde27572cdc0a` | `5d00a35ef92034949f7d05f0f8d07f0df72a0705355e86e144a000e6a6c2632f` |

For all four newly audited ZIPs: raw manifest SHA matches raw CSV bytes; converted manifest SHA matches converted CSV bytes; conversion manifest links to raw SHA; and annual audit SHA matches converted CSV. All four annual `pass` fields are true. Artifact IDs: 2020 `14495458714`, 2021 `14495683436`, 2022 `14496089489`, 2023 `14496558541`.

## Observational demand-only rolling lag references: 2024 vs 2025

Both references score on equal target hours within each year after the first 168 h. The peak decile is defined by the 90th percentile of **actual demand** in the respective year's evaluation window using linear interpolation. These are **retrospective prior-observation** references; no true day-ahead publication-lag claim, model fitting, or ERA5 weather skill.

| Year | Reference | Evaluation target hours | MAE MW | RMSE MW | Mean bias MW | Peak decile MAE MW |
|---|---|---:|---:|---:|---:|---:|
| 2024 | lag-24 | 8616 | 1289.65 | 1849.22 | -4.56 | 2113.49 |
| 2024 | lag-168 | 8616 | 1880.12 | 2851.38 | -2.75 | 4267.44 |
| 2025 | lag-24 | 8592 | 1245.95 | 1749.66 | -0.28 | 1798.95 |
| 2025 | lag-168 | 8592 | 1575.46 | 2241.25 | 4.71 | 3437.32 |

2024 result is the previously reported audited baseline; 2025 is calculated from the authenticated CISO-2025 ZIP, applying the same metrics and 168-hour warm-up. Actual 90th percentile for the target windows: 2024 = 32549.0 MW, 2025 = 31250.9 MW.

No claim of annual improvement is made: the yearly weather, demand, and target distribution differ. Full CISO historical panel now has enough EIA **source coverage** to enter the next stage, but the complete EIA × ERA5 hourly joint panel and fixed train/validation/test skill checks remain pending.

## Cohort accounting

Across the four initially source-verified BA-years (AZPS 2024, BPAT 2024, CISO 2024, CISO 2025) plus four newly independently verified CISO 2020–2023 datasets, the distinct completed total is **8 of the 24 planned BA-years**. Other corrected-wave matrix jobs remain unverified until completed and checked. This is a checkpoint, not an assertion that the full Wave 1 has finished.

C-1 frozen source/results remain unchanged.
