# C-2 BA-0 — Actual source-vintage impact on annual and event demand metrics (2026-11-23)

## Executed empirical audit

Read the **authenticated 210,432-row dual-vintage quarantine data ZIP** in read-only mode. The inner deterministic compressed CSV SHA-256 was `5a7fc7bf030cdac33131c480ca0c145db0b942db050e09bf1c5d1396994dbee1`. The original bulk-CSV-based EIA demand and later EIA v2 API EIA demand are available side by side for **12 BA×years**, without any imputation or forced vintage selection. The other 12 BA×years are **not** treated as matching.

### What the numeric differences actually change

- **174 numeric hourly conflicts** across 12 compared annual BA cohorts. All **12 annual maximum demand values on *common nonmissing paired hours*** were identical between the two vintages; this cannot imply that full-vintage annual maxima agree once differently missing hours are included.
- **AZPS 2025** accounts for **169** numeric disagreements. The difference in sum of hourly power, API minus earlier bulk, is **+33,920 MWh** over 8,760 paired hours (bulk 38,830,649 vs API 38,864,569 MWh, **+0.08735%**). These are 1-hour reported-power sums, not independent measurements of billed annual energy.
- The largest difference in *full-24-hour common-pair UTC daily mean demand* for AZPS 2025 is **1,024.667 MW on July 31, 2025**. Specific bulk -> API readings that day at 19:00/21:00/22:00 UTC: **6569->0**, **6934->273**, **6929->485 MW**. The huge local gaps are a substantive issue for event risk inference even though annual aggregate differences appear small.
- **BPAT 2021/2023** and **CISO 2024/2025** contain many *vintage-dependent missing values*; common-hour calculations necessarily exclude these hours and can mask missing-coverage effects. The previously archived 325-row source-status report is essential to interpretation.
- Full pair-complete UTC days only are used for within-day mean comparison. A single changed hour in an otherwise incomplete day does not contribute to this statistic. No interpolation.

## Reproducible user artifact

`C2_EIA930_Vintage_Metric_Impact_2026_11_23.zip` — SHA-256 `7782396e1b4874111f10e77748b3079471264ea0d591cb538fd8cd61fd261d40`, 6,121,030 bytes; includes immutable dual-vintage source ZIP, Python calculation script, 12-annual-cohort metric CSV, 174 hourly-change CSV, reproducibility README, machine-readable source/approval manifest, **3 locally passing tests**. The ZIP was reopened and contained file bytes were SHA-checked against input files.

## Source acquisition state

EIA officially distributes six-month CSV and API data [EIA-930 information](https://www.eia.gov/electricity/930-content/about.html). The known URL for 2025 Jul–Dec bulk CSV was tried again, but **current original CSV bytes could not be downloaded to this environment**. An independent third-party [Gridprims ledger](https://gridprims.com/ledger/checks/) currently displays matching SHA-256 identifiers for 2025 first and second half original bulk BALANCE files, but this *does not prove a specific revision mechanism or which EIA value is authoritative*. Old bulk vs later API conflicts remain unresolved.

## Formal research restrictions

This is a *descriptive version-sensitivity analysis*, not a fitted forecast or climate attribution test. The ERA5 geographic variable is based on an **unapproved 2018-derived BA boundary candidate**, not a validated operation-year load-weighted exposure. Because 2025 values were already explored, 2025 is **not an untouched blind holdout**. No historic BA geography admission, automatic anomaly replacement, model training, SSP/CMIP6 future scenario modeling or PyPSA stress claims follow from this audit. **C-1 remains frozen.**

**Recommended next gate:** obtain historically byte-matched 2025 EIA bulk CSV or official version release evidence to resolve AZPS 2025, and independently validate dated BA operating boundaries and load-relevant meteorological aggregation. Keep conflicting demand versions isolated meanwhile.
