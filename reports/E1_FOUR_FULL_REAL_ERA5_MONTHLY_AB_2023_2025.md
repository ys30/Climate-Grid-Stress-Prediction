# C2 E1 — Four complete calendar-month real ERA5 HIFLD versus Census BA proxy A/B sensitivity

Date: 2026-11-14 (US Mountain Time). **Project C-2 only; frozen C-1 untouched.**

## Independently observed full-month geospatial source sensitivity

Four full real original public ARCO ERA5 hourly reanalysis 2m-temperature source-month jobs all **SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659672871 .

Full calendar January and July in 2023 and 2025: 4 months × 31 days × 24 real UTC hours × 4 BA = **11,904 direct hourly paired HIFLD A versus Census B geographic temperature estimates**. Each day fetches a *single shared ERA5 24-hour bounding grid* and evaluates both fixed sets of BA candidate polygon cell weights from the same loaded gridded source, avoiding duplicate geospatial data downloads. No EIA demand model fitted or heldout model tested.

A = HIFLD 2018 candidate Control Areas with topology repairs, full-area grid-cell intersection weights SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.

B = independently sourced EIA-861/PUDL 2020–2025 county-membership proxy joined to **fixed 2024 Census TIGER/Line full county geometry**, area weights SHA256 `6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8`.

Both are provisional area-mean meteorological estimands, **neither is an approved historical electricity BA operating-area weather exposure**.

## Actual source monthly mean candidate temperature difference: B − A (°C)

| BA | January 2023 | July 2023 | January 2025 | July 2025 |
|---|---:|---:|---:|---:|
| AZPS | −2.123868 | −1.314399 | −2.060402 | −1.376269 |
| BPAT | +0.259458 | −0.194871 | +0.307063 | −0.206367 |
| CISO | −0.512623 | −0.289539 | −0.481374 | −0.170380 |
| SRP | −1.867336 | −1.807181 | −1.761305 | −1.948729 |

The original four monthly jobs were verified individually as successful, each 2,976 BA-hour source observations. 2023-Jan AZPS 744/744 hourly B−A values were negative, 2023-Jul 744/744, 2025-Jan 744/744, and 2025-Jul 737/744; all **124/124 sampled daily means AZPS were negative**. SRP 744/744 in every month, 124/124 sampled daily means negative. BPAT has winter positive mean and summer negative mean in both years. CISO monthly differences remain negative but are variable, especially in summer.

**These are designed four-month observation windows, not random/independent days and not a complete 2020–2025 climate trend**. Seasonal month/year differences could reflect weather variability and masks, not anthropogenic climate change. Hours/days within selected months are serially dependent and cannot be used as independent confidence-interval draws. The result shows spatial-support sensitivity of real ERA5 reanalysis, not improved predictive performance nor a correct BA operating-territory boundary.

## Traceable archived month source artifacts

- 2023 January: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659672871/artifacts/14139851176
- 2023 July: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659672871/artifacts/14139277607
- 2025 January: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659672871/artifacts/14139422177
- 2025 July: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659672871/artifacts/14139198821

Month-level outputs include original ERA5 matched BA UTC-hour CSVs, daily means, BA summaries and source hashes. `src/c2_era5_AB_monthly_sensitivity.py` implements common-source-grid daily reads, calendar length and exact BA-hour checks, and verifies A/B original SHA256.

Separate reproducible read-only aggregation `src/c2_era5_AB_fourmonth_aggregate.py` verifies the four original files' SHA256, original mask hashes, every BA-hour, input-source geometry flags, and calculation consistency; workflow:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659771480 .
**At the time this report was drafted, the independent aggregation was queued, NOT yet certified successful. Do not count its aggregate artifact until independently verified.**

## Remaining publication gates

- This A/B result addresses *geographic exposure definition* only, and is not an EIA-930 load vs temperature association, let alone anthropogenic climate change attribution.
- Independent EPA/eGRID evidence explains a BA is not strictly a geospatial region; the current HIFLD and whole-county area masks are proxies, not approved electricity-load weighting.
- Stronger spatial proxy would use service location / customer/population-weighted weather with independently validated utility-to-BA data. The 2024 Census fixed boundary used for 2023 / 2025 creates known temporal support approximation.
- The 2020–2025 original EIA-930/ERA5 source panel (210,432 hourly BA records, 260 original demand gaps, 70 anomaly candidates) remains sealed from formal training. 2024–2025 is held out by chronological protocol. Original missing loads are never filled.
- No E2 calendar/GAM/XGBoost forecasts, E3 PyPSA future-grid simulation, SSP scenarios, or ALL/NAT attribution conducted.

**Model admission: CLOSED.**
