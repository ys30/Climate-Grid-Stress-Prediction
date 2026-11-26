# C-2 BPAT — real observed EIA-930 load-tail baseline, 2020–2025 (2026-11-26)

## First new descriptive empirical output this round

All metrics in this report were recomputed **directly from the authentic SHA-locked bulk-vintage EIA-930 BPAT CSV**, not from synthetic rows and not from a prediction model.

- Source `BPAT_2020_2025_EIA930_AUTHENTIC_HOURLY_START_UTC.csv`; SHA-256 `65e51c15227eb9aae84ce65b35038ea458fd8e2fdb6c9608211268e8291761bc`.
- 52,608 unique, contiguous, positive-valued hourly UTC-start demand records from 2020–25; source missing and candidate-anomaly flags are all false.
- Exact, independently recomputed result table committed to `results/source_only/BPAT_2020_2025_EIA930_ANNUAL_DEMAND_DIAGNOSTICS.csv`. Git blob ID in C-2 `735e440b883717e75bc6c2b0a7290b2569af2ffe` **matches the original local result CSV's Git blob hash**. Source-only descriptive analysis, not causal weather results.

| Year | Mean MW | Peak MW | 99th percentile MW | Peak UTC |
|---:|---:|---:|---:|---|
| 2020 | 6,249.41 | 11,742 | 8,525.68 | 2020-11-25 23:00 |
| 2021 | 6,372.46 | 10,123 | 8,951.51 | 2021-12-28 01:00 |
| 2022 | 6,660.56 | 11,068 | 9,318.64 | 2022-12-22 16:00 |
| 2023 | 6,582.67 | 10,693 | 8,951.74 | 2023-01-30 15:00 |
| 2024 | 6,724.26 | 11,496 | 9,521.17 | 2024-01-13 18:00 |
| 2025 | 6,975.31 | 11,537 | 9,661.28 | 2025-02-12 15:00 |

A simple observed 2020-to-2025 **mean** increase of 11.62% is not a causal estimate of global warming: demographic, market, economic, BA reporting and weather variation can contribute. The annual hour-summed original source energy is 54,894,812 MWh in 2020, 61,103,710 MWh in 2025; annual hours vary because 2020/24 are leap years.

## Uniform top-tail definition

Using the single **six-year pooled 99th percentile**, 9,243 MW, and the strict threshold `demand_mw > 9243`: 526 observed hours exceed the threshold, forming 109 maximal contiguous sequences. These sequences have been exported to `BPAT_2020_2025_EIA930_TOP1PCT_EPISODES.csv` in the locally delivered archive. The full-sample threshold is exploratory and not an independent forecast test; do not interpret episodes as weather-driven without ERA5 joint covariates and source QA.

## Important previously unflagged source anomaly candidates

The real 2020 bulk series abruptly rises from **6,803 MW at 2020-11-25 22:00 UTC** to **11,742 MW at 23:00 UTC**, a +4,939 MW change in one hour; the subsequent 24-hour comparison reaches -5,237 MW. The original supplied `EIA930_anomaly_candidate_not_confirmed` flag is FALSE. **That flag is not independent confirmation of physical authenticity**. A 2024-01-11 hour also drops 2,578 MW and rebounds 2,514 MW the following hour. These are **source-review candidates, not automatically invalid observations**; no observations were deleted or modified. Check original EIA source vintage, later API vintage and possible curtailment/interchange/reporting discontinuities before attributing to climate extremes.

The 12 largest absolute within-year one-hour ramps and original flags are in the local `BPAT_EIA930_12_LARGEST_ONE_HOUR_RAMP_SOURCE_REVIEW.csv`. Include an explicitly labeled **with/without-flagged-hour sensitivity** if independent evidence later justifies exclusion; otherwise retain the observed original source.

## Reproducibility and deliverables

Local source-only analysis was run and re-run against the full real EIA input; output CSV hashes and console log were saved. Downloadable ZIP `C2_BPAT_2026_11_26_Verified_Observed_Load_Diagnostics.zip` includes:
- Actual six-year annual diagnostic CSV (SHA-256 `2563760474584f06cf73f446c545727264f9c368ca7edf7774cc0fb3b20a3033`);
- 109-event UTC start/end, duration and max-demand CSV (SHA-256 `360e8aaf005b45aae8be29a35dac1d90f00caf5c30b8dc499ade5ce99d20b4d5`);
- 12 largest hourly ramp review rows (SHA-256 `97c6afcca87c7ff26261a146a0b1ce7dc0641ea836baf346cfe22ce1149eb90f`);
- input SHA and threshold manifest, script and rerun log.
ZIP SHA-256: `b89cec27fda17ed837bc15a4483978e957a8681c06e1d95940ccd381905a8387`, CRC checked.

## Current project scientific gates

- BPA legacy FERC CSV respondent 122 ↔ PUDL respondent 21 ↔ XBRL C002357 is historically cross-verified. **The actual PUDL v2026.10.0 respondent-21 non-imputed hourly rows are still unavailable and no cross-source FERC/EIA MAE or bias is calculated.**
- EIA930 later-API vintage differs in some years and must be reviewed separately.
- Operational historical BA polygon and within-BA county demand weights are unapproved; no weather attribution, CMIP6 scenario or PyPSA stress inference yet.
- A valid next research step using the new *actual* EIA exploratory output is to cross-link extreme episodes to validated ERA5 heat/cold/wind variables, but only after weather-geography/time-zone QA. All model training gates stay **BLOCKED**.
- **C-1 frozen and untouched.**
