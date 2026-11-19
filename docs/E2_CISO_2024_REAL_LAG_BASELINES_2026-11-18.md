# E2 first real-data reference forecast audit — CISO 2024

## Evidence, scope, and no-weather guard

Authentic observed EIA-930 CISO 2024 demand is sourced exclusively from
[successful GitHub Actions run 44427373589](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44427373589),
artifact `14486655626`. Its previously checked UTC-start CSV SHA-256 is
`375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c`.
The annual EIA-only coverage gate passed 8784/8784 UTC hours (2024 leap year).

The data were re-opened from that real artifact ZIP, and the SHA-256 matched.
The metrics below use **only original observed load** (not synthetic forecasts,
ERA5 fields, future climate, or fitted AI). Reproducible scoring script:
`scripts/c2_e2_real_demand_lag_baselines.py`; it refuses any annual file
whose SHA, raw HE clock trace, year or hourly completeness does not pass.

## Equal-sample rolling lag comparison

Targets: 2024-01-08 00:00 UTC through 2024-12-31 23:00 UTC inclusive, the
**same 8616 hours** for both methods (the first 168 hours of the year excluded).
For each hour `t`, score observed `D(t-24)` or `D(t-168)` against `D(t)`.
Past observed values are available retrospectively; the experiment does **not**
claim to simulate a fixed day-ahead or week-ahead delivery timetable.

| Reference | N | MAE (MW) | RMSE (MW) | Bias (MW) | High-load decile MAE (MW) |
|---|---:|---:|---:|---:|---:|
| Same hour previous day (lag 24) | 8616 | 1289.65 | 1849.22 | -4.56 | 2113.49 |
| Same hour previous week (lag 168) | 8616 | 1880.12 | 2851.38 | -2.75 | 4267.44 |

High-load decile is defined by the actual annual evaluation sample:
90th percentile **32,549 MW**. This post-hoc threshold is used solely for
diagnostics, not for model selection. MAE and RMSE denominator is exactly
8616 each; both references have the same target timestamps.

## Interpretation and restrictions

- Within the single CISO 2024 observational cohort, day-lag performs better
  than week-lag on unconditional MAE/RMSE and high-load subset MAE.
- These are **retrospective demand-only reference calculations**, not
  a held-out trained machine learning result. In particular, no claim is
  made about a day-ahead operational forecast without confirming actual
  observation publishing latency.
- Weather response, ERA5 proxy quality, historical climate attribution,
  SSP projections, PyPSA reserve or blackout risk are **not established**.
- Six-year E2 split (train 2020–22, validation 2023, test 2024–25) is
  still blocked until every requisite year and source passes its gate.
- C-1 frozen source/results remain untouched.

## Remaining BA-year source validation

The Wave 1 eight-cohort workflow was committed at
`7820e74510cc968a68cf0935d7a5754a2b381cb0`.
The currently available connector cannot list the automatically spawned
run ID by workflow path. **Do not label Wave 1 as passed** without actual
job logs and artifacts. The validated cohort count remains **1 of 24**.

## Reproduce

Download the CISO 2024 source artifact from the linked GitHub run; extract
`utc_start/eia930_CISO_2024_start.csv` and its adjacent
`eia930_CISO_2024_start.manifest.json`. Run:

```bash
python -m scripts.c2_e2_real_demand_lag_baselines \
  evidence/utc_start/eia930_CISO_2024_start.csv \
  --ba CISO --year 2024 \
  --output evidence/audit/ciso2024_lag_references.json
```
