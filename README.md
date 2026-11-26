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
