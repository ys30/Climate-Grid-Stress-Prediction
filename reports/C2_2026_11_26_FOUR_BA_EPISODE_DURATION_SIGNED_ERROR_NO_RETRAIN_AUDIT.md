# C-2 real source duration-specific extreme-event signed-error audit, 2026-11-26

## Actually executed on earlier frozen observed test-day predictions

Reopened `C2_20261126_Four_BA_Persistent_Event_Paired_Weekblock_Audit.zip` with SHA-256 `e8b38e7402eab3808b9518587e01f8ec511927176671231d8a4e051d9e93dc5f`. The nested event prediction archive was independently CRC-verified. Reused **52,392 authentic previously fitted test-day prediction rows**, **1,271 already identified BA-category-date labels**, and their training-year thresholds. **No model was re-trained, no threshold re-tuned, and no source observations replaced.**

A persistent event is at least two successive complete UTC days of an existing event category inside the *same BA and same test year*. Event duration was split into **2–3d, 4–7d, >=8d**. Signed error = predicted minus actual MW (negative means demand underprediction). Compared calendar versus calendar+REALIZED candidate-area ERA5 within the same Ridge or Huber estimator; the observed future-year weather is an input, **not** an actual forward weather forecast.

Actually reconstructed **15,252 model-event-day records**, matched into **7,626 within-estimator weather/calendar day pairs**, summarized into **210 nonempty BA×target×estimator×event×duration groups**. Examined *true within-episode date contiguity and year boundaries*, duplicate keys, original error identity, all duration assignments, and no blind/geography admission assertions; nine structural and mathematical checks passed. **114 groups** with >=8 episodes were assigned 1,200 episode-cluster descriptive bootstrap draws; **96 groups** with fewer than eight episodes explicitly have no episode interval. These percentiles are **not calibrated scientific confidence intervals**, especially with three previously inspected test years.

### SRP peak, observed high-load persistence

| Duration | Episodes | Days | Ridge weather-vs-calendar delta MAE MW | Huber weather-vs-calendar delta MAE MW |
|---|---:|---:|---:|---:|
| 2–3d | 8 | 17 | **+202.05 (worse)** | **−342.73 (improved)** |
| 4–7d | 5 | 27 | **+174.50 (worse)** | **−257.43 (improved)** |
| >=8d | 6 | 98 | **+143.52 (worse)** | **−291.24 (improved)** |

### New crucial finding: direction matters as much as MAE

On ALL **142 observed-high-demand SRP episode days**, **100% of Huber+observed-weather predictions are BELOW the observed daily peak** (and Huber calendar underpredicts on 100% as well). Huber's smaller MAE in the three groups is *relative to its Huber calendar comparator* and does **not** mean safe or calibrated high-demand forecasting. This underforecast rate is an evaluation **conditional on realized observed high load** classified against the train P95 threshold. It does not establish the unconditional event detection rate or guarantee what happens on unseen forecast-year data.

The 2–3d subgroup has 8 episodes, 4–7d only 5 episodes, >=8d only 6 episodes. A displayed 98 test days cannot be treated as 98 independent weather events. Particularly the 2–3d high-load cohort has very large source-flag-sensitive peaks and an average error of several GW, demanding operator verification before operational alerts.

### Provenance and hard gates

Files in reproducibility archive `C2_20261126_Persistent_Event_Duration_Signed_Error_Repro.zip`: exact locally executed Python `c2_persistence_duration_bias.py`, full **7,626-row matched per-event-day signed-error CSV**, 210-group audit table with MAE/signed bias/underforecast fraction, SRP peak subset, event coverage, checksum manifest, original archived prior event analysis and actual run log. ZIP SHA-256 `ddfd96bde7405a2ea9b28fa9df9cae4897739440614227704f0b246b34b9e0d8`, CRC passed.

The table committed to GitHub is a rounded six-row SRP peak excerpt; complete exact results, code and input are in downloadable ZIP. The historical BA ERA5 geographic mask is still unapproved; original EIA930 spikes are not independently operator certified; genuine 2020–25 FERC714 respondent 21 hourly source is pending. These are nonblind retrospective *conditional weather/load association* diagnostics, not climate causality or CMIP6 SSP/PyPSA prediction results. C-1 remains frozen.
