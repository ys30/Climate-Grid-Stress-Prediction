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

### Mandatory cross-estimator integrity check (2026-11-26)

Before running the event-duration CLI on any actual archived prediction rows, run the independent same-sample gate. It verifies the same observed load and episode label across estimators for every BA/date/target/category key; detects duplicate model rows, gaps, cross-year episodes, singletons and nonfinite measurements; and records the SHA-256 of the exact CSV examined. This script does **not** establish source authenticity or certify weather geography.

```bash
python scripts/c2_cross_model_integrity.py path/to/frozen_episode_pairs.csv --report results/c2_tail/input_integrity.json
# Only if that exits 0:
python scripts/c2_episode_tail_audit.py path/to/frozen_episode_pairs.csv results/c2_tail
python -m unittest discover -s tests -p 'test_c2_*.py' -v
```

The six integrity-unit tests were locally executed and passed before their GitHub commit; that does not establish that GitHub Actions has passed or that authentic 7,626-row inputs have been audited. Never label synthetic test fixtures as empirical observations.

### Safe one-command C2 episode audit

**Use the validated entrypoint** rather than running the lower-level metrics script on its own:

```bash
python scripts/c2_run_validated_audit.py frozen_episode_pairs.csv results/c2_tail_run_001 --bootstrap 1200
```

The command requires complete Ridge+Huber estimator coverage on every BA/date/target/event-category key, matching observed MW and episode IDs, and contiguous >=2-day episodes. An invalid input is rejected **before new metrics are produced**. A directory already holding `episode_duration_metrics.csv` is rejected to prevent mistaking stale prior output for a new run. Each successful run saves `input_integrity.json`, `episode_duration_metrics.csv` and `audit_manifest.json` with input SHA-256 and retrospective/nonblind evidence label.

**Not an empirical execution:** the new CI fixtures are constructed test examples. The previously described 7,626 paired event-day records and source-flagged SRP peaks must be recovered from the actual archived ZIP before scientific numbers are recomputed. An observed-weather hindcast is not an issue-time forecast. Full source authenticity and geography approval remain pending.

### Snapshot-safe C2 audit gate (2026-11-26 follow-up)

The validated runner now copies the input CSV bytes to an immutable *run-local snapshot* **before** applying integrity checks and computing metrics. Results are staged in a temporary directory and published only after the final manifest and integrity report are complete. If a destination directory exists, or the computation errors, no completed output is published at that location. The manifest includes the SHA-256 of the actual snapshot used for metrics. This protects against changing input between validation and scoring and against partial/stale outputs.

The source-integrity gate also checks that Ridge and Huber have identical source-flag status for matched BA/date/target/event-category records, and refuses unknown flag values. The tests include mismatched flags, absent model rows, existing output folders, and injected computation failure. All tests are synthetic software checks; **they are not historical SRP validation**.

The wrapper's atomic publication was smoke-tested in an isolated local harness, but GitHub Actions success still requires confirmation from the actual repository workflow. The original 7,626 matched event-day records are not included in this repository update.

### Recovering the genuine archived 7,626 event-day pairs

A read-only, **locally unit-tested** archive inspector is available at [`scripts/c2_archive_inventory.py`](scripts/c2_archive_inventory.py). It verifies the ZIP SHA-256, checks each ZIP member CRC, rejects traversal-like entry paths, and reports CSV columns and row counts **without modifying historical source records**.

```bash
python scripts/c2_archive_inventory.py C2_20261126_Persistent_Event_Duration_Signed_Error_Repro.zip \
  --sha256 ddfd96bde7405a2ea9b28fa9df9cae4897739440614227704f0b246b34b9e0d8 \
  --output results/c2_source_inventory.json
```

The SHA above comes from the existing archive report, not from a newly recovered local archive. If the hash mismatches, stop rather than silently switching archives. The expected source analysis includes **7,626 within-estimator matched weather/calendar day pairs**, which are not necessarily 7,626 separate BA/date keys and are not automatically in the new audit-runner schema. The inspector does NOT transform or certify the full input. Only after documenting the actual CSV schema can an explicit, checked adapter be developed. The four archive unit tests passed locally on synthetic ZIP fixtures; original-source archive recovery remains pending.

### EIA-930 four-BA reported forecast benchmark: source retrieval and real-data workflow

New [official-source collector](scripts/c2_fetch_eia930_df.py) retrieves EIA API v2 hourly original values `D` and `DF` in BA × month chunks, verifies the API-returned total, rejects duplicate keys, writes a SHA-256 source manifest, and refuses to overwrite old runs. It **does not** invent or impute missing demand. The four target BAs are CISO, AZPS, BPAT, and SRP. Run with `EIA_API_KEY` from your environment (do not commit this key):

```bash
python scripts/c2_fetch_eia930_df.py results/c2_eia930_source_2023_25 --start-year 2023 --end-year 2025
python scripts/c2_eia930_day_ahead_benchmark.py \
  results/c2_eia930_source_2023_25/eia930_D_DF_hourly.csv \
  results/c2_eia930_df_2023_25 --ba CISO --ba AZPS --ba BPAT --ba SRP
```

Also available: [manual GitHub Actions source-and-benchmark workflow](.github/workflows/c2-eia930-reported-forecast.yml). Configure repository secret `EIA_API_KEY` if required, then dispatch the workflow for the desired complete historical years; it archives raw export, source manifest, daily metrics, incomplete-day waterfall, and output manifest. The offline collector tests require no API access. **No live EIA extraction or operational skill number is claimed from adding this code/workflow.**

EIA publishes values using the hour-ending convention (source: https://www.eia.gov/electricity/930-content/about.html). Our initial daily metric is a complete **UTC** 24-hour demand peak, *not* BA-local operating day. Distinguish the historical reported DF series from a verified original forecast issuance vintage; ERA5 realized-weather predictors remain hindsight inputs. External acquisition is blocked in the current isolated environment, so independent BA-year data coverage and comparisons to the 142 SRP event dates are still pending.
