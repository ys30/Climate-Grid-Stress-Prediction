# Climate-Grid Stress Prediction (C-2)

Independent research on historical weather–electricity responses and future climate-conditioned grid stress in the Western US.

**C-1 is frozen.** Source repository: https://github.com/ys30/Climate-Grid-Resilience-Research at immutable commit `6b549a6612f280646389f87bfc35453dd0e5d7dc`. No C-1 result is modified or promoted to observed outage evidence.

## Status (2026-11-26)
Historical EIA-930 × ERA5 data and retrospective four-BA load evaluation now exist, including 2023–2025 held-year Ridge/Huber comparisons, previously inspected source-quality diagnostics, and an original-source persistent-event duration/signed-error audit. **These are retrospective, nonblind comparisons using realized ERA5**; they are not issue-time forecasts, proof of climate causality, CMIP6-driven demand projections or calibrated PyPSA adequacy results.

The latest audit finds that SRP Huber underpredicted observed daily peaks on **all 142 observed-high-load persistent-event days** (19 independent episodes). The MAE difference from the Huber calendar-only comparator may improve with realized weather yet systematic high-tail underprediction persists. Original SRP source spikes and BA weather geography require independent review; no source-flagged anomalies should be silently removed.

**Next-stage frozen design:** [E2→E3 extreme forecast admission protocol](reports/C2_E2_E3_EXTREME_FORECAST_ADMISSION_PROTOCOL_2026_11_26.md). Read the [duration/signed-error audit](reports/C2_2026_11_26_FOUR_BA_EPISODE_DURATION_SIGNED_ERROR_NO_RETRAIN_AUDIT.md). All uninspected future validation, forecast issue-time weather, data-identity and extreme-load reliability gates are explicitly **not yet passed**.

## Scientific tracks
A. Weather-driven historical associations and counterfactual weather normalization; separate long-term anthropogenic climate attribution only when a defensible climate counterfactual is supplied.
B. Out-of-time validated weather–electricity predictions, downscaled CMIP6-driven forecasts, and assumption-conditioned PyPSA stress screens.

Read [protocol](docs/RESEARCH_DESIGN.md) and [source inventory](docs/SOURCE_AUDIT.md). Run `python -m unittest discover -s tests -v` for initial guardrails. No historical data files are stored in this initial commit.

## Executable C2 persistent-event tail audit (2026-11-26)

The standalone standard-library CLI [`scripts/c2_episode_tail_audit.py`](scripts/c2_episode_tail_audit.py) audits **already frozen, pre-labeled persistent episodes and already calculated predictions**. It does **not** fit a model, discover an event, fetch official data, or validate future forecast weather.

Input CSV required headers:
`ba,date,target,estimator,event_category,episode_id,actual_mw,calendar_pred_mw,weather_pred_mw`.
Optional: `source_flag` (1/true/yes/y/flagged). `date` must be ISO YYYY-MM-DD. Provide one row per BA/date/target/estimator/event category. All episode IDs must represent >=2 consecutive days in the same calendar year; invalid inputs fail closed.

```bash
python scripts/c2_episode_tail_audit.py path/to/frozen_episode_pairs.csv results/c2_tail --bootstrap 1200 --seed 20261126
python -m unittest discover -s tests -p 'test_c2_episode_tail_audit.py' -v
```

Outputs: `episode_duration_metrics.csv` and `audit_manifest.json`. Metrics include original and weather-assisted MAE, calendar-versus-weather signed error, underforecast fraction/severity, day-weighted versus episode-weighted delta MAE, and episode-cluster descriptive bootstrap percentiles for >=8 episodes. The audit **does not produce prospective skill or scientifically calibrated confidence intervals**. CI: [C2 episode audit tests](.github/workflows/c2-episode-tail-audit.yml). Executing the CLI requires the genuine archived prediction CSV converted to the specified schema; the code does not fabricate or bundle the original 7,626-row archive.
