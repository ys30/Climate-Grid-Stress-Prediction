# C-2: REAL four-BA extreme-event retrospective Ridge/Huber validation (2026-11-26)

Actually executed on original 210,432 EIA930×candidate ERA5 four-BA hourly source (ZIP SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`); 8,732 complete BA×UTC days. Three earlier-year-training/later-year-test splits, 2023–2025. Ridge(alpha=10) and Huber(epsilon=1.35, alpha=10) fixed; original-source full training and testing days preserved. Calendar-only and calendar+observed test-year candidate ERA5 temperature regressors compared. Training-only reference climatology and scalers.

Evaluation-only event groups use **training-year-only** candidate daily temperature anomaly P10/P90 and training-year load target P95 thresholds. Test-day actual loads used solely to identify the high-observed-demand *scoring cohort*, not as predictors or for thresholds. All source anomaly flags retained; no input rows removed. Conditions overlap and tail groups can be sparse.

Actual outputs: **52,392 test-day prediction rows**, **36 BA×testyear×target threshold records**, **1,088 model×event score rows**, **544 same-estimator weather/calendar paired score rows**. A Python audit recomputed each nonempty event group's n and MAE from the 52,392-row prediction ledger; verified no duplicate threshold configuration, timing and provenance, source flag preservation, and prior SRP original peak result (**8 substantive checks passed**). Bundle ZIP `C2_Four_BA_20261126_EventStratified_Ridge_Huber_RealSource_Backtest.zip`, ZIP SHA-256 `c2b786d98a9f63043516aedd7144aa2600e2bac1613852597b27c2d0199f2d5e`, CRC passed. Includes actual source ZIP and executed scripts, outputs, checks and logs. GitHub stores the key SRP peak summary separately; full raw daily prediction ledger is in bundle, not yet hosted in the repo.

### SRP daily peak results: mean of individual test-year subgroup MAEs (MW)

| Segment | Ridge calendar | Ridge+observed weather | Huber calendar | Huber+observed weather |
|---|---:|---:|---:|---:|
| All days | 1304.84 | 1320.02 | 819.70 | **736.30** |
| Cold tail (train anomaly P10) | 2640.43 | 2379.50 | 2003.94 | **1786.80** |
| Warm tail (train anomaly P90) | **1296.61** | 1598.65 | 1347.28 | **1071.41** |
| High actual demand (train target P95) | **2604.47** | 2738.10 | 3007.70 | **2735.90** |

Candidate ERA5 improves same-estimator test-group MAE in 65/72 cold-tail comparisons, 59/72 warm-tail, 70/72 high observed-demand, 68/72 full all-days across BA×year×target×estimator. **These comparisons are dependent and do not establish independent statistical significance.** Among high-load days, Huber calendar and Ridge calendar comparisons are not necessarily matched to identical loss estimators; no universal 'best model' claim is warranted.

Interpretation: robust Huber avoids much of SRP's Ridge failure without deleting original flagged hours; *however absolute SRP high-demand MAE remains around 2.7 GW*. Known original SRP spikes are still not independently source-certified. Test-year weather is observed, not forecast. Historical data repeatedly inspected: **nonblind retrospective**. Candidate weather geography not operator-approved; FERC714 respondent21 genuine hourly demand and CMIP6+PyPSA forecasts are NOT substantiated. Formal model training and historical causal attribution blocked. C-1 frozen.

Next: compute event error stability with within-BA rolling week blocks, stress-test thresholds, pursue operator-certified BA weather geography and EIA/FERC demand source validation. Do not post-select Huber merely on these inspected years.
