# C2 E2 operational forecasting benchmark: EIA-930 D / DF

Status: **new method and locally tested synthetic fixture; NOT yet executed on official archived hourly observations**. No effect size or real-data improvement claimed.

## Data discovery, not climate attribution

EIA's Form 930 documents both observed reported demand and BA-produced day-ahead demand forecasts. Official documentation: https://www.eia.gov/electricity/930-content/about.html . API browser: https://www.eia.gov/opendata/browser/electricity/rto/region-data . API endpoint: `https://api.eia.gov/v2/electricity/rto/region-data/data/` .

Export the `D` (realized demand) and `DF` (reported day-ahead forecast) series for identical BA codes and 2023–2025 periods, preserving `period,respondent,type,value`, source retrieval date, URL/query and original response file checksum. The new standard-library program works on an **already downloaded** CSV (no network, no embedded API key):

```bash
python scripts/c2_eia930_day_ahead_benchmark.py raw_eia_930_D_DF.csv results/eia930_df_2023_2025 --ba SRP --ba CISO --ba AZPS --ba BPAT
python -m unittest discover -s tests -p 'test_c2_eia930_day_ahead_benchmark.py' -v
```

**Do not silently equate** a final historical EIA DF record with the original forecast vintage issued by a BA: track revision history and issue timestamps where available. This is an *operational reported-forecast benchmark* with potential revisions, not proof that a model using realized ERA5 is a true day-ahead forecast.

## Data integrity and target alignment

1. Pair `D` and `DF` by identical `respondent` and UTC hour-ending `period`; convert hour-ending to interval-start using a one-hour shift for daily UTC aggregation. Confirm the relevant API's period semantics against official downloadable files before headline claims.
2. Keep complete 24-hour **UTC** days only; preserve excluded-day denominators. An operational **BA-local day** benchmark is a separate analysis requiring explicit reporting timezone and DST (23/25 local-hour days).
3. Store both `max_hour D` vs `max_hour DF` daily peak error and DF at the **actual** D peak hour; these are different estimands. Report both alongside hourly MAE and mean signed bias.
4. Never compare EIA `DF` daily peak against a model defined with a different BA, target, UTC/local day, hour coverage, missingness sample or electricity demand definition.
5. For the already inspected SRP 142 event days, join on `BA × UTC date × outcome` **only after** independently validating hourly source definitions. These observations are a *post-hoc comparison cohort*, not an unseen operational benchmark.
6. Daily observed-high-demand conditional underforecast fractions are not event-detection precision or recall. For true warning skill, define the alert threshold and decision horizon on training data, and evaluate all eligible forecast days.
7. Do not insert EIA's reported operator `DF` into the Ridge/Huber model as a predictor without pre-registering a distinct information set. Otherwise the comparisons become circular.

## Acceptance gates before claims

- Public EIA source export and raw source SHA manifest captured.
- Both actual and DF report coverage audited by BA and year.
- Hour-ending/clock convention verified, 24-hour UTC and BA-local DST robustness documented.
- Historical DF revision/vintage caveats recorded.
- Forecast issue-time weather input obtained separately; realized ERA5 models labeled hindsight/weather-conditioned.
- Full paired scorecards and worst underforecast episodes published; no flagged peaks silently removed.
- C1 frozen; E3 CMIP6 and E4 PyPSA not promoted without their own validation.

C2 current evaluation in `reports/C2_2026_11_26_FOUR_BA_EPISODE_DURATION_SIGNED_ERROR_NO_RETRAIN_AUDIT.md` is an earlier **retrospective nonblind** weather/calendar comparison, not validation against EIA DF.
