# Project C-2 — E1 complete six-year real-source hourly panel (2020–2025)

Updated 2026-11-14. This report concerns **C-2 only**. C-1 remains frozen.

## Scientific scope

All 72 calendar months across 2020–2025 have been retrieved and independently reconciled from **real public ARCO ERA5 gridded hourly reanalysis (2m temperature)** and **official EIA-930 original balancing-authority reported demand**, for AZPS, BPAT, CISO and SRP. The geographic area weights refer to four 2018-vintage source-derived **unapproved candidate control-area masks**, not vetted 2020–2025 EIA operating-area boundaries.

One hour of ERA5 2m *reanalysis* is a real numerical reanalysis product, not a direct thermometer/station measurement. The weighted temperature is a provisional area-estimate, not an approved BA electricity-load exposure.

### Verified end-to-end CI

- 18 Feb/Apr/Oct month jobs, all successful: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43627785579
- 42 remaining source-month jobs: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43627845540 (36 non-December jobs succeeded, 6 December jobs failed from exclusive-end-year date logic; **do not count these failed December jobs**).
- All six repaired December source months passed independently: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43628125103
- Archived January 2020–2025: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43619234662
- Archived July 2020–2025: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563497776 and https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43563639298
- **Complete six-year consolidation SUCCESS**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989
- **Download the complete hourly CSV.gz, 72-month summary, source gap CSV, anomaly candidate CSV and SHA-256 manifests**: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989/artifacts/14127710411 . Artifact ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`.

## Actual six-year source completeness — all 72 actual months audited

| Year | Real ERA5 2m BA-hours | Nonmissing EIA-930 demand × ERA5 pairs | Original EIA demand missing BA-hours | EIA demand anomaly *candidates* |
|---|---:|---:|---:|---:|
| 2020 | 35,136 | 35,061 | 75 | 6 |
| 2021 | 35,040 | 35,010 | 30 | 1 |
| 2022 | 35,040 | 35,036 | 4 | 28 |
| 2023 | 35,040 | 35,036 | 4 | 33 |
| 2024 | 35,136 | 35,040 | 96 | 0 |
| 2025 | 35,040 | 34,989 | 51 | 2 |
| **Total** | **210,432** | **210,172** | **260** | **70** |

Per BA, actual source weather hours are **52,608 each**, including both leap years 2020 and 2024. Original demand missing BA-hours: AZPS 26, BPAT 0, CISO 109, SRP 125. The 70 candidate anomaly events remain **candidates**, not confirmed errors; they are listed by BA, UTC timestamp and raw demand value in the artifact's `source_EIA930_anomaly_candidates_NOT_CONFIRMED.csv`.

The 260 original missing source demand slots are preserved as blank in the unified source CSV.gz and separately listed in `source_EIA930_missing_demand_hours_NO_IMPUTATION.csv`. No demand or weather interpolation was performed. Nonmissing demand does not itself imply data are verified for modeling: candidate anomalies require review.

Actual data archive file:
`C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz`

SHA256 of **this inner gzipped CSV** (distinct from the outer Actions ZIP digest):
`88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

The all-source archive uses deterministic gzip compression with no embedded timestamp, sorted year/month/BA/time and source-linked SHA256 for every monthly input CSV and original EIA-930 source half-year. All row-level fields explicitly declare `geometry_historically_approved=False` and `model_training_eligible=False`. No supervised learning/causal attribution is included.

## Critical scientific gate: REAL SOURCE ≠ VALID BA METEOROLOGICAL EXPOSURE

The 2018 source-derived national Control Areas polygon matches are:

| BA | Source OID | Original topology | Pilot area-weight cells |
|---|---:|---|---:|
| AZPS | 23 | invalid; make_valid sensitivity candidate | 265 |
| BPAT | 4 | invalid; make_valid sensitivity candidate | 1,557 |
| CISO | 11 | invalid; ring self-intersection | 662 |
| SRP | 36 | valid | 55 |

- CISO's derived candidate `make_valid` area differs about **7.08%** from an invalid original polygon area computation (a topology diagnostic, *not* measured boundary drift).
- AZPS/SRP source candidate masks overlap by ~**96.66% of SRP's polygon area**. They are not mutually exclusive partitions, and we must verify EIA BA operating areas separately from administrative/control service territory data.
- Source YEAR 2018 does not prove time-stable representativeness of the weather exposure for 2020–2025.
- Four source BA masks describe land area, not necessarily load-weighted population or assets; use multiple exposure definitions and a documented BA temporal crosswalk. A single masked ERA5 spatial mean cannot be asserted as a validated electricity-load weather driver.

Therefore **the real source panel is collected and fully audited, but the *model-ready* historical panel is not admitted yet**. `c2_weather_join.py` and `c2_temporal_gate.py` reject model admission without independently documented geographic/vintage/temporal QA. This is deliberate and must not be bypassed.

## Next tasks needed for publication-quality work

1. Review alternative historical BA-area GIS provenance from independent sources and reconcile with EIA-930 BA operator identity; define a **geography admission memo** addressing dated boundaries, CISO source topology and AZPS/SRP near-containment, plus a sensitivity exposure scenario.
2. Review 70 candidate anomalous demand hours against official source and EIA reporting conventions. Existing 260 absent EIA demand hour slots must stay explicitly missing.
3. Freeze source data archive provenance and prepare durable public deposition (e.g. Zenodo) only with proper source citation and differentiated code/data licensing. GitHub Actions artifacts are **temporary**.
4. Once the independently documented geography and QA gates pass, build and independently validate the final 2020–2025 analytic panel. Chronological splits remain train=2020–2022, validation=2023, held-out test=2024–2025.
5. Then fit calendar baseline/GAM/XGBoost weather-demand response and separately design historical climate attribution (ALL vs NAT forcing, meteorological variability vs climate change). Future CMIP6 SSP and PyPSA system stress projections are separate later stages.

**No empirical model accuracy, anthropogenic causal effect or SSP grid-stress result is claimed in E1.**
