# C2 E1 — real ERA5 four seven-day geography sensitivity: independently verified 2,688 BA-hours

Updated: 2026-11-14 (US Mountain Time). C-1 repository frozen; C-2 repository only.

## Verified data source, experimental estimands and execution

Four independent real public Google ARCO ERA5 0.25-degree 2m reanalysis temperature windows were retrieved and fully paired under two different candidate BA-area masks. No EIA-930 demand is modeled in this experiment.

- A: 2018 HIFLD Control Area topology-repair candidate, 0.25-degree area weights SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.
- B: actual EIA-861/PUDL BA annual county-membership × Census TIGER 2024 full county-union mask, area weights SHA256 `6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8`.
- Actual UTC windows, 168 hours per BA each: Jan 15–21 and Jul 1–7 in 2023 and 2025. Four BAs = 4 weeks × 168 hours × 4 BAs = **2,688 real matched-hour temperature comparisons**, all original hourly ERA5 observations present under both proxy masks.
- Every individual real-source job **SUCCESS**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43656511154 .
- Separate original artifact ingestion, source SHA256 and exact BA-hour verification job **SUCCESS**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43656652099 .
- Consolidated downloadable CSV (2,688 hourly differences; four-BA summary; source manifest): https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43656652099/artifacts/14138411533 . Outer GitHub artifact digest SHA256: `7252a7fa0c6edf0a4a97efe4689bbb143a1948e85b6335ee372b7b835d91868e`.

## True empirical observations

Differences are **T_B - T_A, °C**. Each row is a directly matched ERA5 source grid hour processed under different source-derived geographic weights; not two independently observed physical weather series.

| BA | 2023 Jan 15–21 mean | 2023 Jul 1–7 mean | 2025 Jan 15–21 mean | 2025 Jul 1–7 mean |
|---|---:|---:|---:|---:|
| AZPS | −2.013979 | −1.358161 | −2.491822 | −1.542771 |
| BPAT | +0.196529 | −0.066082 | +0.401649 | −0.248561 |
| CISO | −0.486569 | −0.204731 | −0.518613 | −0.238134 |
| SRP | −1.980443 | −1.639726 | −1.768533 | −2.055429 |

Combined across the 4 designed weekly windows, each BA has 672 hourly ERA5 spatial-proxy comparisons:

| BA | Mean (B−A) °C | Median °C | Minimum °C | Maximum °C | Hours with B colder |
|---|---:|---:|---:|---:|---:|
| AZPS | **−1.851683** | −1.749332 | −3.391983 | −0.679393 | **672/672** |
| BPAT | +0.070884 | +0.102963 | −0.546101 | +0.746584 | 271/672 |
| CISO | −0.362012 | −0.367974 | −1.002001 | +0.230019 | 601/672 |
| SRP | **−1.861033** | −1.864524 | −3.810149 | −0.515423 | **672/672** |

AZPS and SRP spatial temperature estimates remain notably sensitive to support geometry in these *specific* sampled winter/summer weeks. BPAT's temperature difference reverses direction between sampled winter and summer weeks. CISO is modestly cooler under B in most sampled hours. This supports including an explicit geography/exposure-sensitivity section in C-2 and carefully evaluating its eventual consequences for predictions.

## Rigorous scope and limits

The sample contains four *selected* seven-day windows. Adjacent hours are strongly autocorrelated, so **672/672 is not 672 independent experiments**. No p-value or confidence interval based on independent hourly observations is justified. The comparisons do not establish average differences for all hours of 2020–2025, nor prove HIFLD A or Census B is historically representative of EIA-930 electricity balancing-area operating territories.

2024 TIGER county geometry was held fixed for the observed 2023 and 2025 weather comparisons. EIA-861 county memberships have annual support, but whole-county boundaries and customer/load weather exposure remain approximations. National HIFLD polygons from YEAR 2018 have original topology issues, and the AZPS/SRP source areas nearly overlap in the original SRP geometry. Never enforce mutually exclusive BA territories without audited reporting evidence.

EPA documents that balancing authorities are not strictly geographically based. A weather predictor weighted by census counties is an independently sourced *candidate* geographic estimand, not a validated superior BA operating area.

**Model admission remains CLOSED.** All E1 source geo records remain `historical_geography_approved=false` and `training_permitted=false`. The complete original 2020–2025 EIA-930/ERA5 source panel (210,432 BA-hours, 260 missing original-demand values, 70 anomaly candidates) is preserved and not refit. No GAM/XGBoost forecast model, historical ALL/NAT climate attribution, future SSP or PyPSA stress projection is reported.

## Next methodologically valuable steps

1. Repeat A/B at longer month-level real ERA5 windows and quantify day-to-day and diurnal variability; avoid treating serial hourly records as independent.
2. Test independent and temporally appropriate load-relevant geography/weights against both proxies, e.g. census population or annual EIA-861 customers with a verified utility-to-BA crosswalk and documented uncertainty. **Do not promote B to an approved BA polygon automatically.**
3. Freeze reproducible PUDL source release/version and original Parquet SHA256 (the existing yearly PUDL county crosswalk currently derives from a mutable `nightly` source).
4. For any eventual E2 prediction, agree an admissible weather-exposure estimand, perform leave-period-out sensitivity checks, exclude or review 70 demand anomaly candidates, retain 260 missing source-demand hours without imputation, and keep 2024–2025 chronological holdout sealed until model design is frozen.
