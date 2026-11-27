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

### EIA-930 complete UTC day correction and BA-year coverage (2026-11-26)

The API `hourly` frequency is UTC; the original BA reporting view can use BA-local time. The EIA record is hour-ending. Therefore a **complete UTC date** requires hour-ending stamps `01:00` through **next day's `00:00`**. Earlier collector monthly windows `01T00..lastT23` missed the final complete UTC date of every month and included a previous-month spillover hour. The collector now requests `month-01T01..next-month-01T00` inclusive. See [EIA's technical documentation](https://www.eia.gov/opendata/documentation.php), [EIA-930 reporting notes](https://www.eia.gov/electricity/930-content/about.html), and the [collector](scripts/c2_fetch_eia930_df.py).

The new [BA-year coverage scorecard](scripts/c2_eia930_coverage_scorecard.py) distinguishes complete 24-hour paired days, incomplete days, and **entirely absent dates** (which do not appear in either daily output CSV). It reports coverage denominator of 365/366 days, annual daily-peak MAE, mean signed bias and high-load-underforecast fraction computed only for complete observed days, and marks every partial BA-year explicitly. The manual [real-data workflow](.github/workflows/c2-eia930-reported-forecast.yml) now archives `ba_year_coverage.json` along with raw hourly input and daily benchmark. Tests added for leap years, month-boundary exact 24-hour windows, missing whole days and duplicate dates.

No real-data retrieval, GitHub Actions success, or operator forecast performance is inferred from these software changes. For a BA's **local operating-day** evaluation, timezone/DST (23/25-hour days) must be treated separately rather than treating the UTC calendar day as an operational definition.

### Automatic real-source pilot: SRP July 2025

An [SRP July 2025 EIA-930 D/DF pilot workflow](.github/workflows/c2-eia930-srp-pilot.yml) was added. A push touching that workflow or the two related source/benchmark scripts triggers it automatically, with an independent manual dispatch option. It **first** runs offline parser tests, **then** requires the repository's `EIA_API_KEY` Actions secret, downloads one month of original hourly D and DF for SRP, scores daily peaks, and checks for at least 25 complete UTC days out of 31. All available pilot artifacts are uploaded even if later steps fail. The pilot is an API/data-alignment acceptance test, **not** an independent validation of model skill or the 142 historical SRP event days.

To limit source acquisition rather than treating missing configuration as scientific negative evidence, `scripts/c2_fetch_eia930_df.py` now supports `--month 7` and fails with an explicit missing-key error before requests. The EIA API documentation requires a registered API key: https://www.eia.gov/opendata/documentation.php .

**Gate remains open:** no authentic hourly source download, BA coverage, or verified GitHub Actions pass has been observed in this chat. Review the Actions execution result and `pilot/source/source_manifest.json` plus `pilot/daily/eia930_df_daily.csv` before reporting a real value.

### Source authenticity gate for official EIA-930 pilot (2026-11-26)

The SRP pilot and four-BA workflow now run [`scripts/c2_verify_eia930_source.py`](scripts/c2_verify_eia930_source.py) **before** computing any D/DF scorecard. This checks the saved source CSV SHA-256 against the original retrieval manifest, exact record counts against API totals and each BA×month export, proper UTC hour-ending month assignment (including a first-of-next-month 00:00 record), duplicate keys, permitted respondent/type values, and invalid values. A failure stops the scoring workflow; available pilot artifacts can still be inspected to diagnose it.

The verifier has [five synthetic fixture regression tests](tests/test_c2_verify_eia930_source.py), incorporated into the CI workflow. A separate regression guard ensures blank/null EIA hourly values mark incomplete UTC days rather than crashing or being silently treated as zero.

This validates the *integrity of the downloaded file against its manifest*, **not** the true original forecast issuance vintage or the truth of reported EIA data. No successful live pilot, final BA-year performance estimate, or empirical 142-day join is claimed until the official workflow produces and retains its actual output.

### SRP pilot failure diagnosis and official non-API source option

The [SRP July 2025 live pilot](.github/workflows/c2-eia930-srp-pilot.yml) now writes `pilot/diagnostics/step_outcomes.json` and a GitHub Actions step summary with **which stage failed**: API-key preflight, original data fetch, source manifest verification, 24-hour scoring, or coverage gate. The artifact upload runs even on error. These diagnostics intentionally never expose the value of `EIA_API_KEY`.

**Before concluding an API bug:** first inspect the exact failed step. In particular, a missing `EIA_API_KEY` repository Actions secret is a configuration failure, not an observed electricity-data quality failure. Push-triggered run conclusions cannot be recovered from a commit status with an empty status array.

**Official alternative without API requests:** EIA also offers six-month `Balance` CSV downloads on the [EIA Hourly Electric Grid Monitor / About EIA-930](https://www.eia.gov/electricity/930-content/about.html). Balance files include actual hourly demand and day-ahead demand forecasts; archive the original downloaded CSV and hash, then explicitly map its clock fields and BA identifiers into the normalized `period,respondent,type,value` format. The six-month raw file is **not** automatically the same API schema and should never be passed to the normalized scoring script without checking those mappings. A manual downloaded balance CSV is a real-data alternative if GitHub secrets or EIA API access remain unavailable.

Current CI caveat: workflow code is committed, but this conversation has not retrieved the actual push-run job logs or produced genuine EIA-930 pilot source artifacts, so the real root cause and successful pilot status remain unconfirmed.

### EIA-930 pilot failover update: official public bulk Balance archive

The [SRP July 2025 pilot](.github/workflows/c2-eia930-srp-pilot.yml) now has two **real**, EIA-origin source routes: (1) official EIA APIv2 when the GitHub Actions `EIA_API_KEY` is configured and collection succeeds; (2) the **public, keyless** EIA six-month `EIA930_BALANCE_2025_Jul_Dec.csv` archive when the API key is absent or the API fetch fails. The second source is documented on the [official EIA-930 About page](https://www.eia.gov/electricity/930-content/about.html).

The [bulk adapter](scripts/c2_fetch_eia930_bulk.py) explicitly maps `Balancing Authority`, `UTC Time at End of Hour`, `Demand (MW)`, and `Demand Forecast (MW)` to normalized `period,respondent,type,value`. It filters one BA and one **complete UTC** month, preserves null demand/forecast values as missing (never zero), retains the **original six-month EIA CSV bytes** along with normalized rows, and publishes hashes for **both**. [Source verification](scripts/c2_verify_eia930_source.py) checks the original raw bulk SHA-256 and normalized dataset SHA-256; **a bulk manifest never fabricates API pagination totals**. The source's `origin` is always recorded, allowing results to be separated by original API vs six-month CSV provenance. Code failures remain explicit and scored results cannot be published until the integrity gate passes.

Local source CSV replay without an API key:
```bash
python scripts/c2_fetch_eia930_bulk.py results/srp_july_2025 \
  --year 2025 --month 7 --ba SRP --bulk-file /path/to/EIA930_BALANCE_2025_Jul_Dec.csv
python scripts/c2_verify_eia930_source.py \
  results/srp_july_2025/eia930_D_DF_hourly.csv \
  results/srp_july_2025/source_manifest.json
```

This change addresses a **known dependency risk** (API key availability / API collection failure) without claiming it caused the previously observed failure. The current chat still has not retrieved the actual push-run logs or executed a successful live EIA request; the latest public bulk route must pass the GitHub workflow and be checked against its uploaded original-source artifact before any empirical findings are reported.

#### SRP pilot operational failure recovery (follow-up)

After repeated uninspectable push-run failures, the July 2025 SRP pilot now **does not require an EIA API key**: it attempts API ingestion only if a secret is present and automatically falls back to EIA's public historical `EIA930_BALANCE_2025_Jul_Dec.csv` when the API step is skipped or fails. The optional API attempt has a **180-second limit**, leaving runtime for the public fallback; repeated pushes cancel older in-progress pilot jobs. A passing downstream score is gated on the source manifest and complete UTC-day requirement, not on availability of the API secret.

Bulk workflow output preserves the original six-month raw CSV, derived SRP one-month normalized D/DF CSV, both SHA-256 hashes, manifest, source verifier report and daily scorecard. If both API and public EIA download fail, the workflow should still **fail visibly**, with per-step status diagnostics, rather than fabricate an EIA result. Run-level success and true empirical results remain unconfirmed until actual Actions logs and artifacts are inspected.
