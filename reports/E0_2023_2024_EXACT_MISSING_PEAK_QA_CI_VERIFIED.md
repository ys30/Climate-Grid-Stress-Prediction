# C2 E0 exact missing-hour and raw peak audit — source CI verified (2026-11-12)

## Execution
- Success: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43312300904
- Separate 2023 and 2024 matrix jobs using BOTH EIA930 official semiannual BALANCE CSVs; tests plus source inspection passed.
- Full per-hour output artifacts: `exact_missing_hour_keys.csv`, `raw_peak_candidates.csv`, `annual_quality.csv`, `quality_manifest.json`.
- No source values were imputed, silently clipped or relabeled as observed outages.

## Raw 2023 annual maximum timestamps (UTC interval start)
| BA | Maximum raw reported demand MW | Timestamp UTC |
|---|---:|---|
| AZPS | 9,854 | 2023-04-27 20:00 |
| BPAT | 10,693 | 2023-01-30 15:00 |
| CISO | 44,007 | 2023-08-17 01:00 |
| SRP | **70,313 (suspect; not accepted as physical peak)** | **2023-06-03 20:00** |

## Raw 2024 annual maximum timestamps
| BA | Maximum raw reported demand MW | Timestamp UTC |
|---|---:|---|
| AZPS | 11,308 | 2024-01-23 18:00 |
| BPAT | 11,496 | 2024-01-13 18:00 |
| CISO | 47,571 | 2024-09-06 01:00 |
| SRP | 8,356 | 2024-08-04 23:00 |

## Source missingness
- 2023 exact missing/blank BA-hours total: **34** (7–8 absent timestamp keys per BA; 4 blank/invalid observed values in total).
- 2024 total: **126** (7–8 absent timestamp keys per BA; 96 blank/invalid reported values in total, evenly CISO and SRP).
- No duplicate BA-hour keys in either audited year.
- Inspect exact missing dates and neighboring values in the artifact before event-window admission. The annual 99% coverage result DOES NOT license interpolation through a heat wave or an unverified spike.

## Next
The diagnostic workflow was further updated at `e4cbe3b85188e1770e8daceadee4a8b5f87c9050` to print raw top-observation neighbor contrasts and early missing hour keys directly in logs. Await its CI before asserting any particular anomalous neighboring values or root cause. SRP 70,313 MW is a **quarantined candidate**, not a validated observed peak.

### Causal and prediction boundaries
Weather responsiveness and anthropogenic climate attribution cannot be inferred from this QA; 5 CMIP6 SSP scenarios and PyPSA grid stress cases remain downstream plans only.
