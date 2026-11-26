# C-2 | Four-BA six-year deletion sensitivity of daily demand metrics (2026-11-26)

## Executed on authentic input, not synthetic FERC or forecast data

This turn re-opened the actual original archive `C2_2020_2025_72_Month_Original_Source_Archive.zip` (SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`), and source gzip `C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz` (SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`). All 210,432 original BA×hour rows were verified unique. Only UTC days containing 24 nonmissing original EIA930 hourly demand readings and 24 candidate ERA5 temperatures entered the daily model. BA weather geometry remains **unapproved**.

Model: within each BA, year×month demeaned daily load target (peak, intra-day P95, daily mean), regressed by least squares on month-year demeaned piecewise cold/warm daily-mean candidate temperature anomaly. The 2 terms are separately residualized by year×month. No causal or operator-approved climate inference is permitted.

### Actually executed fit grid

Four BAs × winter/nonwinter × 3 outcomes × 2 QA variants (original vs source-flagged UTC days omitted for **sensitivity only**) × 7 source partitions (all years and leave each one of 2020–2025 out) = **336 real-data fits**, 48 estimator summaries.

All **7 locally run checks passed**, including original archive SHA, complete estimator grid, all six omissions, no causal/admission status, source-reproducible BPAT and AZPS results. This is **deletion sensitivity, not new unseen held-out model validation**; 2025 has been repeatedly inspected in the project.

### Winter cold-association response in MW per °C

| BA | Daily target | Original full 6-year cold slope | Min–max when omitting exactly one year |
|---|---|---:|---:|
| AZPS | peak | 21.02 | **5.00–77.24** |
| AZPS | intra-day P95 | 61.42 | **57.67–65.37** |
| AZPS | mean | 43.21 | 40.15–45.83 |
| BPAT | peak | 184.99 | 177.41–193.14 |
| BPAT | intra-day P95 | 180.90 | 173.19–189.63 |
| BPAT | mean | 152.03 | 143.57–159.32 |
| CISO | peak | 194.67 | 181.20–206.45 |
| CISO | intra-day P95 | 204.32 | 195.37–216.54 |
| CISO | mean | 178.39 | 152.87–191.35 |
| SRP | peak | 35.47 | **17.83–60.62** |
| SRP | intra-day P95 | 68.18 | 46.97–82.19 |
| SRP | mean | 39.73 | 35.05–46.33 |

In all 48 estimator configurations, each of the 6 year-deletion estimates **retained its original sign**. Sign consistency does not imply model validity, physical causal identification, or stable magnitudes. AZPS original winter daily peak is extremely year-sensitive; under source-flagged-day omission, the winter peak slope is 69.00 MW/°C, and its six year-deletion results range 63.41–73.80 MW/°C. SRP original peak is also year-sensitive. The original daily peak must continue to be reported but cannot be the only robustness target.

### Auditable exact-result deliverables

Self-contained local `C2_20261126_Four_BA_Daily_Indicators_336_LOYO_SourceLocked.zip` contains:
- Exact original source archive used in calculations;
- Exact locally executed `loyo_daily_targets.py`;
- Complete **336-row** CSV and **48-row** model summary CSV;
- `MANIFEST.json` with original and derived SHA-256;
- Execution log, source-data checks and **7/7 passed** test log;
- README.

Local bundle SHA-256 **`423772153d194c965d0c95a19173856501f41996703d6e18f3b03318b72720fd`**, ZIP CRC OK. GitHub winter summary: `results/source_only/C2_FOUR_BA_2020_2025_DAILY_TARGET_LOYO_WINTER_UNAPPROVED.csv`. The local archive contains the exact tested script; **do not interpret the Github summary CSV as an independent CI execution**.

### Admission and next stage

This strengthens the **measurement and model sensitivity** component but leaves the same hard data blockers: historic BA operating geography not approved, original API-vintage spikes and SRP anomalies not operator-certified, actual PUDL v2026.10.0 respondent 21 FERC hourly demand unavailable, no permitted historical climate attribution, no verified future SSP/PyPSA stress result. The next substantive study phase needs a pre-specified model protocol before fitting BA×Season×Temp interactions, with time dependence and source-quality gates explicit. **Project C-1 frozen.**
