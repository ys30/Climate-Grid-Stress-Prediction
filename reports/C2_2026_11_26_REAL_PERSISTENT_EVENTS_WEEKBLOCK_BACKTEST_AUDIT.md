# C-2 | Actual four-BA consecutive event evaluation on 2023–25 held-year predictions — 2026-11-26

## New executed result

Input: SHA-locked earlier `C2_Four_BA_20261126_EventStratified_Ridge_Huber_RealSource_Backtest.zip` SHA256 `c2b786d98a9f63043516aedd7144aa2600e2bac1613852597b27c2d0199f2d5e`; its original 2020–25 EIA930×unapproved candidate ERA5 source archive remains included in the reproduction bundle. The analysis directly read **52,392 rows** of real year-held-out test-day predictions. Neither Ridge nor Huber was retrained, retuned or selected anew. Thresholds were previously computed on earlier training years only: daily candidate temperature anomaly below training Q10 or above Q90, and observed daily demand above training P95.

**New event persistence definition**: at least **two consecutive eligible complete UTC days** in the *same BA and same test year*, within one of the above three classifications. Weather categories and high-load categories may overlap. Thresholds and earlier models do not use observed test-year demand in training; high-load event labeling is evaluation-only, retrospectively using observed load.

Event ledger: **1,271 BA-category-date labels** (overlap allowed), BA × 3 event category counts 12 rows; paired test-day model-error comparisons **7,626** records (2 estimators × 3 load targets × all persistent event labels); 72 BA×target×estimator×event group summaries. 800 week-block resamples of *paired daily absolute-error differences* within each group; these ranges are illustrative dependency stress tests, **not confidence intervals** under the repeatedly inspected years. All eight audit groups passed, including exact reconciliation to the stored original observed/predicted test-day records and event-run contiguous/within-year checks.

## SRP, daily peak, pooled eligible persistent event DAYS (MW MAE)

| Persisting event | Ridge calendar | Ridge observed-weather | Huber calendar | Huber observed-weather |
|---|---:|---:|---:|---:|
| At least two consecutive cold-tail days (95 days, 31 episodes) | 2740.20 | **2474.13** | 2117.35 | **1910.90** |
| At least two consecutive warm-tail days (130 days, 33 episodes) | **1274.21** | 1569.07 | 1334.07 | **1067.50** |
| At least two consecutive actual high-load days (142 days, 19 episodes) | **1482.53** | 1638.95 | 1862.06 | **1571.08** |

**Difference from previous source report:** This experiment pools all eligible persistent event days for a group; the previous non-consecutive-event report reported an *equal mean of three separately computed test-year cohort MAEs*. Thus SRP high-load numbers ~1483/1639 here versus ~2604/2738 earlier cannot be interpreted as a direct change in prediction model performance: the event inclusion criteria AND weighting differ. Model predictions are unchanged.

### Descriptive week-block stability for SRP peak WEATHER minus CALENDAR paired absolute errors

| Event | Ridge pooled difference MW | exploratory block percentile range MW | Huber difference MW | exploratory block percentile MW |
|---|---:|---|---:|---|
| Cold | -266.07 | [-386.70,-142.23] | -206.45 | [-390.70,-11.08] |
| Warm | **+294.86** | [+129.13,+469.43] | **-266.57** | [-481.47,-71.68] |
| High-load | **+156.42** | [+59.68,+262.75] | **-290.98** | [-349.76,-234.82] |

Within all four BAs × 3 targets = 12 BA×target pairs, Huber weather improves paired MAE for **12/12** cold, **12/12** warm and **12/12** persistent high-load strata. Ridge weather improves **11/12** for each; notably SRP is unfavorable for warm and high-load. These counts are correlated and exploratory, **not independent statistical tests**.

### Provenance and limitations

Local actual script `c2_event_persistence_audit.py`, test `test_c2_event_persistence.py`; result rows re-derived and audited against original prior real test predictions. Verified local bundle `C2_20261126_Four_BA_Persistent_Event_Paired_Weekblock_Audit.zip` SHA256 `e8b38e7402eab3808b9518587e01f8ec511927176671231d8a4e051d9e93dc5f`; CRC passed, includes exact SHA-locked original event-backtest bundle, runnable scripts, CSVs and metadata. GitHub only stores aggregated result; local original code and source records in bundle.

These results concern **observed test-year candidate weather**, not forecasts and not independent 2025 blind test. Source extrema are not operator certified and historic BA ERA5 geography is not approved. No formal climate attribution, new FERC 714 respondent21 original-hour validations or SSP/PyPSA future stress simulations have been done. C-1 remains frozen.
