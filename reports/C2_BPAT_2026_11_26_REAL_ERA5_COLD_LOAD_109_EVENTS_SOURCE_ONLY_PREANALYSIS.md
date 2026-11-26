# C-2 BPAT — first six-year authentic EIA930 × candidate ERA5 extreme-load co-occurrence (2026-11-26)

## What was ACTUALLY executed

Directly re-read the source-backed `C2_2020_2025_72_Month_Original_Source_Archive.zip` from current workspace, verified full ZIP SHA-256 **bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504**, and extracted original member `C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz` (source gzip SHA-256 **88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac**).

Filtered actual `ba == BPAT` to **52,608 unique UTC-start hours** in 2020–25 with **52,608 nonmissing original EIA930 demand MW** and **52,608 nonmissing source-backed candidate-area ERA5 2m air temperatures**. Verified both flags `geometry_historically_approved == False` and `model_training_eligible == False` for every hour.

The observed original EIA930 demand pooled six-year empirical 99th percentile is **9243 MW**; a strict `>9243` comparison selects **526 high-load hours**, arranged into **109 contiguous UTC-hour episodes**.

## Descriptive temperature anomaly definition (NO causal interpretation)

Calculate each hourly ERA5 candidate-area temperature anomaly as its observed temperature less the six-year sample mean candidate-area temperature for the **same month × UTC clock hour**. This adjusts only seasonal month and hour mean, **not** climate trend, load growth, source vintage, weather-geographic uncertainty, demand electrification or correlated days. It is not a formal counterfactual, seasonally detrended causal model or untouched holdout.

- **516/526 (98.1%)** of high-load hours occur during November–March.
- **389/526 (74.0%)** have a candidate-area temperature anomaly ≤ **−5 °C**; **7/526 (1.3%)** show anomalies ≥ **+5 °C**.
- Of **109 events**, **71** contain at least one ≤−5 °C anomaly hour and **60** consist entirely of ≤−5 °C anomaly hours. The longest continuous exceedance is **64 hours**, starting **2024-01-12 14:00 UTC**.
- Denominators for candidate-temperature anomaly groups (all observed BPAT hours):
  - cold ≤−5 °C: **389/4,957 (7.85%)** high-load;
  - neutral (−5,+5) °C: **130/43,509 (0.299%)** high-load;
  - warm ≥+5 °C: **7/4,142 (0.169%)** high-load.
  These are descriptive conditional frequencies under strong seasonal/autocorrelation dependencies. **Do not interpret their ratio as attributable risk or causal temperature effect**.
- High-load hours by year: 2020 **10**; 2021 **62**; 2022 **99**; 2023 **44**; 2024 **137**; 2025 **174**. The full-sample threshold and increasing demand mean this is **not** a held-out performance measure or climate trend evidence.

## Source anomaly sensitivity and eligibility

The original unflagged 2020-11-25 23:00 UTC **4,939 MW one-hour source load jump** spans a suspect four-hour >P99 burst through 2020-11-26 02:00 UTC. Keeping 9243 MW and monthly-hour temperature reference fixed, *sensitivity-only exclusion* of those four hours leaves **522** high-load hours with the same **389** candidate cold hours (share **74.5%** vs **74.0%** original). **Main output retains all four hours; there is no verified reason to delete them.**

The original historical BA geographic proxy is explicitly **unapproved**, so this is a **preliminary exploratory co-occurrence signal only**. It cannot justify a geographic exposure attribution, climate-change effect, temperature-response causal coefficient, forecasting claim, or PyPSA power-system stress model. Candidate temperature can differ under alternative historical BA footprints; no significance test is implied because hours cluster within storms.

The 2020–25 BPA FERC714 respondent 21 real source hourly data is still **not authenticated/retrieved**. BPAT original EIA930 vs later API source-vintage discrepancies, historical operator-certified BA territory, within-BA load weights and FERC/EIA scope equivalence remain scientific gates.

## Reproducible result package and files

Local ZIP `C2_BPAT_2026_11_26_Real_EIA_ERA5_Cold_Load_Exploratory.zip`, SHA-256 **055403122dd91ee741c79d67d3e88fdc40e34bd90f7bd76e9a133bf655fe8302**, ZIP CRC verified. Contains the executed `analyze_bpat_era5_extremes.py`, README, direct execution log, source/full output SHA manifest, 6-year annual summary, **109-row UTC event and proxy-temperature ledger**, and cold/neutral/warm event-hour denominators. Re-run against the pinned original archive for full verification.

Key GitHub summary tables (not independently approved inference):
- `results/source_only/BPAT_2020_2025_ERA5_CANDIDATE_EXTREME_LOAD_ANNUAL.csv`
- `results/source_only/BPAT_2020_2025_ERA5_CANDIDATE_COLD_WARM_BANDS.csv`

**Next scientific steps:** compare alternative candidate weather masks (HIFLD/TIGER subset + external BA territory information), quality-control 2020 source spike and EIA vintages, study *event-level* cold/heat weather co-occurrence accounting for month/hour and serial dependence, and finally complete independently measured FERC714 respondent 21 coverage. **C-1 remains frozen.**
