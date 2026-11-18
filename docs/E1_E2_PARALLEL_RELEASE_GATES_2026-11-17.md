# C-2 E1→E2 parallelization decision and release gates — 2026-11-17

## Decision
The independently reconciled utility-county *retail-sales* analysis does **not** identify a unique county spatial allocation: the observed multi-county utility energy may not be split by population, county count, or an NLR model-derived county profile and then described as observed county load. Keep this work in E1 **spatial-weight evidence pending**. This is not a blanket prohibition on a separate BA-level EIA-930 demand prediction track.

## Parallel, non-circular E2 pilot (admitted conditionally)
1. **Outcome:** sourced EIA-930 hourly *reported BA demand* for CISO, AZPS, BPAT, SRP. Explicitly do not interpret as all end-use retail electricity sales or local county loads.
2. **Exposures:** ERA5 temperature/humidity from spatial grids using transparent, geography-only uniform-area BA proxy or preregistered point/grid aggregates; label them proxy exposures, NOT demand-weighted BA temperature. Since BA shapes do not always follow counties, area proxies must document geometry validity and weather-grid coverage. Do not take NLR population/BA-derived county profiles as independent exposure truth.
3. **Data contract:** timezone and hour-ending normalization to UTC interval start, monotone unique (BA, UTC hour), missingness/gaps and revision audit, reporting semantics, BA-era geography, input provenance/hash, calendar joins, annual hour counts and unit checks. Never use future weather or target values unavailable at forecast issue time.
4. **Prerequisite for fitting:** >=3 complete annual cycles in the actual joint EIA-930 × ERA5 panel; source-backed hour/BA coverage; explicit chronological splits with no mixing of the same heatwave across training/validation/test. Proposed train 2020–22, validation 2023, test 2024–25 only if all passes; else adjust chronologically *before* training, and document eligibility. No synthetic fallback.
5. **Benchmarks:** calendar/seasonal naive, degree-day regression, GAM/segmented distributed lag; boosted tree only as the third core family if data gates pass. Report BA-year-season and peak-decile MAE/RMSE/bias, blocked bootstrap CI and relative skill to calendar naive.
6. **Sensitivity that must be shown:** alternative exposure grids/aggregation, temperature/humidity, dropped anomalous reporting weeks, predeclared unusual weather periods, alternative time controls. Neither SHAP nor feature importance alone establishes causal effects.
7. **Claims:** may say held-out **BA demand prediction** only after performance verification; weather-normalized historical associations are conditional on exposure proxies and controls; climate-caused demand and anthropogenic contribution remain **unidentified** without a defensible ALL/NAT climate counterfactual.

## County-mapping release gate (separate from BA pilot)
A county load-weighted exposure / county attribution claim requires *independent* metered or utility-verified service-area/county kWh evidence, reconciled within BA-year totals and valid vintage. Utilities spanning multiple counties require source-documented splits or retain bounds. The NLR 2016–23 estimated county hourly product may be a comparison benchmark but is not observed truth and can be circular with BA-level load. For each new external evidence source record: utility ID, FIPS support, vintage, original units, public URL, retrieval date, license, source SHA, measured-vs-estimated status, mapping rule, reconciliation residual, and claim admissibility.

## Future scenario work permitted before E2 skill gate
Build an **inventory-only** GCM × SSP × variable × daily-grid × years coverage table, with source/version checks, SSP1-1.9 cross-product comparability, calendar definitions, reference 1995–2014 and future 2041–2060; no forecast figure, model skill or PyPSA risk estimate is claimed. Do not convert daily extremes into hourly coincidence without validated downscaling.

## Release table
| Track | Work allowed now | Blocked claim / required proof |
| --- | --- | --- |
| E1 utility/county | utility priority ranking, external meter/service evidence, marginal county bounds | unique county kWh until external allocation evidence |
| E2 BA data | independent EIA-930 × ERA5 complete-case inventory, QA, baselines after coverage pass | verified forecast skill until genuine held-out evaluation |
| E2 historical response | preregistered weather normalization after E2 predictive validation | anthropogenic attribution without ALL/NAT |
| E3 climate | source metadata and scenario comparability audit | calibrated future hourly climate/load without out-of-time skill and hourly conversion validation |
| E4 PyPSA | code/parameter audit and synthetic solver tests clearly labeled | blackout probabilities, observed EENS, or physically validated capacity stress until physical input gates |

## Implementation checklist
- [ ] Reconcile and publish a per-BA, per-year EIA-930 hourly outcome × ERA5 exposure inventory with provenance.
- [ ] Define BA proxy weather aggregation reproducibly with geometry limitations.
- [ ] Explicitly block any retail county allocation model-derived weights from BA pilot features.
- [ ] Predeclare chronological split and selected forecast horizon before training.
- [ ] Run three baseline model families with leakage tests, per-BA held-out diagnostics and blocked confidence intervals.
- [ ] Separately record top utility external evidence for ambiguous county MWh.
- [ ] Perform SSP/GCM source coverage audit without publishing scenario predictions yet.

This document supplements `docs/RESEARCH_DESIGN.md` without modifying the frozen C-1 results or relaxing the existing fail-closed gates.
