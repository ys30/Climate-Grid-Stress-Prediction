# C2 E1 — Three independently sourced real ERA5 geography proxies A/B/C

Verified on 2026-11-14 / 2026-11-15 UTC; Project C-1 remains frozen and unchanged. **The official BA-weather model geography gate is CLOSED.**

## Census source C successfully built: formerly blocked source pipeline resolved

Previous Census PL94-171 API failed returning HTML `Missing Key`; the official bulk Census Population Estimates Program `co-est2025-alldata.csv` was used instead. This dataset's variable `ESTIMATESBASE2020` represents **April 1, 2020 population estimates base** and is NOT the 2020 decennial PL P1 actual enumeration, nor electricity customer counts.

Confirmed actual original Census source build **GitHub CI SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43665930801 .
Official data URL:
https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv

- Original Census CO-EST2025 CSV: 2,071,735 bytes; SHA256 `4f5a499d851e2cb48fd7a5405e5a9235453a8a66933657aacd10df0e264f35d5`.
- 182 distinct actual US Census source county FIPS joined to valid Census TIGER/Line 2024 county geometry.
- TIGER 2024 original ZIP SHA256 `04e668d3502757c837c13444730547cd967f28a2c49aeffb873d1792ab2cb97b`.
- EIA-861 annual county source membership CSV SHA256 `6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68`.
- Proxy C area-allocated county population ERA5 0.25° grid weights frozen CSV SHA256 `741d9e1b1101b6a018311803dee6e42fda8b5dacf26ccf40e876171383335361`.
- Download population source counts, county-to-ERA5 weights, and provenance:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43665930801/artifacts/14142580281 .

| BA | EIA-861 source counties | 2020 estimated resident population base | Candidate ERA5 population-weighted grid cells | Per-BA normalized weight sum |
|---|---:|---:|---:|---:|
| AZPS | 15 | 7,158,104 | 522 | ~1.0 |
| BPAT | 109 | 12,883,152 | 1542 | ~1.0 |
| CISO | 58 | 40,014,445 | 819 | ~1.0 |
| SRP | 3 | 4,904,563 | 99 | ~1.0 |

Populations are **not mutually exclusive BA load-customer totals**; the three SRP county memberships overlap the AZPS county set. The density of residents is assumed uniform **within each county**, not within a BA. Each cell's estimate is allocated by exact intersection with the Census TIGER polygon projected to equal-area EPSG:5070 and normalized within the BA.

## Actual first four UTC-hour weather samples with all three unapproved spatial masks

**CI SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43666406669 .
Download verified 16 BA-hour A/B/C source output:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43666406669/artifacts/14142500400 .

A: HIFLD2018 area weather; B: Census2024 EIA861 county-area weather; C: Census2020 *estimates-base* county-population weighted ERA5 weather, with same 2024 county geometry. True original public ARCO ERA5 hourly 0.25° reanalysis 2m temperatures are held constant across all three spatial integrations.

Table lists **T_C − T_B** in °C at exactly 12:00 UTC on the specified dates:

| BA | 2023 Jan 15 | 2023 Jul 1 | 2025 Jan 15 | 2025 Jul 1 |
|---|---:|---:|---:|---:|
| AZPS | +3.703586 | +4.778047 | +4.977613 | +5.573019 |
| BPAT | +3.249993 | −1.520875 | +4.414678 | −0.958344 |
| CISO | +3.124503 | −1.033990 | +2.928709 | −1.272011 |
| SRP | +1.141248 | +2.429895 | +1.683898 | +2.354768 |

At this sample, Census population-weighted temperature differs markedly from area-weighted temperature; seasonal sign reversal for BPAT/CISO does not imply climate change or a customer-weighting error. The sample comprises 4 deliberately selected UTC hours, not independent climatological tests. **Neither A nor B nor C has been approved as representative of historical EIA-930 BA electricity demand geography**.

## New longer real-data protocol (not yet counted complete)

The real four complete diurnal days (2023/2025 Jan15 and Jul1) under A/B/C have been submitted in `src/c2_era5_ABC_four_day.py` and `.github/workflows/e1-real-ERA5-ABC-four-day.yml`. The workflow reads a common real ERA5 24-hour weather grid per day, requires 288 source proxy-hour records per day and outputs 384 BA-hour A/B/C matched comparisons total.

CI workflow:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43666836001 .

**At writing this new job is queued, so no hourly diurnal A/B/C ranges or means are claimed.** Results must be explicitly verified from run logs and artifact digest before reporting.

## Scientific gating and publication restrictions

The study source panel of six years of real EIA930 × ERA5 data (210,432 candidate BA-hour records; 260 original reported-demand gaps and 70 demand anomaly candidates) remains unchanged and **not model-admitted**. C represents resident population estimates-base distribution, **not actual electricity service meters, kWh, peak demand, customer counts, generation, or load distribution**, and has unresolved county-internal heterogeneity. The 2020 estimate base uses 2024 polygon geography, and all county membership is a proxy for BA service territory, not an official map of BA electricity dispatch jurisdiction.

Source geography status and training flag stay `False`; no GAM/XGBoost E2 model training, ALL/NAT historical climate attribution, CMIP6 SSP projections, or PyPSA system stress experiments are claimed. If further population-weighted A/B/C results remain consistent over longer windows, they demonstrate only **spatial exposure sensitivity** until an independently accepted load-relevant geographic estimand is documented.

C-1 remains frozen.
