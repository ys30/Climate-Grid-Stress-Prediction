# C2 E2 → E3 admission protocol: extreme-load forecast validity (2026-11-26)

Status: **PREREGISTERED NEXT-STAGE PROTOCOL, NOT EXECUTED RESULTS**. This document does not change C1 or backfill a successful future forecast.

## Why the current observed-weather experiment is not deployment-ready

- Latest archived source audit: [duration-specific signed-error audit](C2_2026_11_26_FOUR_BA_EPISODE_DURATION_SIGNED_ERROR_NO_RETRAIN_AUDIT.md).
- Four-BA 2023–2025 held-year evaluation was **retrospective and previously inspected**; ERA5 for the later test years was *realized* weather, not an issue-time weather forecast.
- SRP observed high-demand persistent peak events: 19 episodes / 142 event days across duration strata (2–3d: 8 episodes, 17 days; 4–7d: 5, 27; >=8d: 6, 98). On those 142 event-days, both the Huber calendar and observed-weather models underpredicted the actual peak on 100% of days.
- With weather minus calendar MAE, SRP Ridge worsened by +202.05/+174.50/+143.52 MW (2–3d/4–7d/>=8d); SRP Huber improved by −342.73/−257.43/−291.24 MW. Relative improvement does not prove reliable peak calibration.
- The >=8d class has only six independent episodes. Event days are not independent replications; descriptive episode resampling must not be labeled inferentially calibrated confidence intervals.
- Original EIA-930 load spikes, SRP operator interpretation, FERC-714 respondent-21 2020–2025 source, and BA ERA5 geography remain unresolved. Preserve source flags; never silently remove adverse rows.

## Frozen hypotheses before evaluating another uninspected future test block

H1: Compared to a calendar-only model of the SAME estimator, weather features improve overall MAE on unseen years and across BAs, not only on already inspected event strata.

H2: The weather model does not increase **underprediction frequency or severity** among high-demand episodes. A lower MAE is not evidence for H2 by itself.

H3: Results are not sensitive to a few source-flagged observations, HIFLD/Census geography choices, or leakage through training-year features.

H4: Any future CMIP6→PyPSA demonstration is *assumption-conditional*; it may be labeled predictive only after the temporal, geometry, source, and calibration gates below pass.

## Split design and nonblind boundary

1. Preserve current 2023–2025 evaluations as **development / post-hoc**. They must never become a new blind test because thresholds and results were already inspected.
2. Identify an **uninspected later test period** only if real load and correctly time-stamped forecast-weather inputs exist; alternatively, conduct a *clearly labeled* frozen-protocol replication in another BA/region with independent source validation. Record exact acquisition dates and decision timestamps.
3. Before accessing held-out outcomes, freeze: response variable (hourly/daily peak), candidate area map, training reference period, sample inclusion and source flags, feature definitions, missingness handling, hyperparameter selection, estimator list, random seeds and code/data SHAs.
4. All scalers, lag windows, climatological normals, heat thresholds, event thresholds (including P95), imputers and hyperparameters are fit using training blocks only. No realized test-year reclassification of *forecasted* events.
5. Use temporal nested validation for hyperparameters, then train once on the pre-declared training window. Include calendar-only seasonal naive plus calendar Ridge and Huber as same-split comparators. The observed-weather analysis must remain a separate **perfect-weather hindsight upper-information scenario**, not an operational forecast claim.
6. A true forward test requires weather forecasts available by each prediction issue time and a stated lead horizon. ERA5 reanalysis of the target day is not eligible as forecast weather.

## Required outcome metrics (all BAs, years, and episodes)

- General: sample counts, coverage, MAE/RMSE/mean bias for each target, model, and weather-input regime.
- Tail: signed error = predicted minus observed (MW), underforecast fraction (signed error < 0), mean and quantiles of negative error magnitude, P90/P95 observed-demand conditional MAE, maximum contiguous underforecast run, and duration-specific comparisons.
- Episode: define episodes as >=2 successive complete days within SAME BA, SAME test year and train-frozen event category; report 2–3d/4–7d/>=8d, number of **independent episodes**, episode-mean metric and day-weighted metric side by side.
- Paired comparator: weather-minus-calendar delta for same BA, test day, target, estimator, and exact sample; negative MAE delta means improvement. For bias, show both values, not only a delta.
- Detection: separately compute precision/recall and lead-time event detection *only* for predicted-event thresholds fixed on training data. Conditioning on observed high demand cannot estimate true event alert recall on the population without specifying the prediction rule.
- Uncertainty: use episode/block-aware descriptive bootstrap with the same cluster resampled across paired models. Show raw episode count and withhold intervals if <8 episodes; clearly flag previously inspected test sets as nonblind.

## Mandatory data and geography QA

- Independently compare official raw EIA-930 timestamps, balancing-authority codes, demand units, revision flags and extreme spikes with retrievable operator or FERC-714 evidence. Do not reinterpret unexplained spikes as physical demand.
- Document hourly UTC vs BA-local clock, DST handling, repeated/missing hours, leap days, daily aggregate completeness, BA membership and geographical proxy uncertainty.
- Rerun pre-specified results with original data intact, with *flagged-only* sensitivity (not a preferred deletion), and with both alternative BA candidate-area proxies. Report geographic mask version and grid-cell weights.
- Publish denominator waterfall at each data merge and source coverage by BA/year. Report missing source years rather than filling them with model-generated values.

## Formal gates

**Gate E2-A source identity:** source timestamps, BA definitions, observed load spikes and geography traceable and independently reviewed.

**Gate E2-B temporal generalization:** frozen protocol applied to genuinely uninspected period/independent region, with no test leakage; realized weather labeled oracle/hindsight when used.

**Gate E2-C extreme reliability:** no unacknowledged systematic dangerous tail underforecast; metrics and raw exceptions published, with sensitivity to flagged records and episode clustering.

**Gate E3 climate shift:** CMIP6 selection, SSP/GCM composition, bias correction performed only using calibration reference, variable-specific transfer checks and extreme-tail shift quantified; report uncertainty by GCM/SSP/period and geography, not just pooled samples.

**Gate E4 PyPSA:** observed generation capacities/BA interfaces, load validation, resource profile and demand response calibration, feasibility and solver checks; future adequacy values remain scenario-based screens without independently supported physical inputs.

Do not unlock E3 headline forecast/causal attribution or E4 calibrated grid adequacy claims unless their specific gates are met.

## Implementation checklist (no pass implied)

- [ ] Pin immutable data, model, script, manifest and full artifact checksums in repo.
- [ ] Recover and operator-review original flagged EIA-930 SRP peaks and FERC-714 counterpart.
- [ ] Perform complete BA/year/hourly merge and mask QA on frozen definitions.
- [ ] Write event-level paired signed-error tests, with zero-episode and sparse-group gates.
- [ ] Pre-register exact next genuinely uninspected target block and forecast issue-time inputs.
- [ ] Freeze code before evaluating target; archive full error and event tables, not only selected excerpts.
- [ ] Only then expand CMIP6/SSP to future load and PyPSA stress simulations.

C1 repository stays frozen at `6b549a6612f280646389f87bfc35453dd0e5d7dc`.
