# C2 E1 — Four real seven-day ERA5 population vs area geographic sensitivity windows

Verified on 2026-11-14/15 UTC. Project C-1 unchanged and frozen. **Formal geographic/model admission remains CLOSED.**

## Observations and actual source provenance

This study compares genuine public Google ARCO ERA5 2m temperatures using the exact same hourly grid for three distinct *unapproved* BA spatial proxies:

- **A** — HIFLD YEAR-2018 Control Area repaired-candidate polygon area-weighted ERA5, archived weights SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.
- **B** — annual EIA-861 BA-to-county membership × Census TIGER/Line 2024 county polygons, area weighted, archived weights SHA256 `6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8`.
- **C** — SAME B counties and same 2024 polygons, but county resident population weight based on official Census Vintage 2025 county `ESTIMATESBASE2020` (April 1, 2020 population estimate base), assumed uniformly distributed *within each county*. Archived weights SHA256 `741d9e1b1101b6a018311803dee6e42fda8b5dacf26ccf40e876171383335361`.

C is *not* a utility customer, building meter, peak-load or energy weighted geographic exposure. The 2020 estimates base and 2024 county geometry intentionally have different vintages. EIA-861 annual BA-to-county lists do not define precise operational BA electricity footprints.

Four preselected actual UTC windows, all 168 contiguous hours each:
2023 Jan 15–21, 2023 Jul 1–7, 2025 Jan 15–21 and 2025 Jul 1–7. Every observation compares A, B and C against a single common actual ARCO ERA5 0.25-degree 2m weather grid for that hour.

**All four real-data seven-day jobs SUCCESS:**
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43668145338 .
Four BA × 4 source windows × 168 actual hours = **2,688 real A/B/C BA-hour matched source records**.

## Empirical mean C − B differences, °C

| BA | 2023 winter Jan 15–21 | 2023 summer Jul 1–7 | 2025 winter Jan 15–21 | 2025 summer Jul 1–7 |
|---|---:|---:|---:|---:|
| AZPS | +4.948541 | +3.882591 | +5.483331 | +4.467344 |
| BPAT | +3.910286 | −0.961972 | +4.166072 | −1.715333 |
| CISO | +3.572720 | −2.419534 | +3.128945 | −1.616961 |
| SRP | +2.003025 | +1.652065 | +1.821202 | +2.030672 |

Hourly sign audit per 168-source-hour week:
- AZPS: population C warmer than B in **168/168** real hours in all four windows.
- SRP: population C warmer than B in **168/168** real hours in all four windows.
- BPAT: C warmer in 168 winter 2023, 53 summer 2023, 168 winter 2025, 9 summer 2025.
- CISO: C warmer in 168 winter 2023, 0 summer 2023, 168 winter 2025, 9 summer 2025.

This is a strong reproducible **description of spatial exposure weighting sensitivity**. No generalization to all 2020–2025 hours or independent-per-hour statistical inference is warranted. Adjacent weather hours are autocorrelated, four windows were selected rather than randomly sampled, and weather C is not empirically validated against actual BA load distribution.

The same A/B/C source weights were used in the earlier four 24-hour diurnal sample result:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43666836001 ,
384 verified real BA-hour comparisons with first 24-hour source result:
AZPS mean C−B +4.814620°C, BPAT +0.595046°C, CISO +0.390574°C, SRP +1.964409°C.

## Independent frozen source audit

`src/c2_era5_ABC_fourweek_aggregate.py` validates four exact archived source weeks, 2,688 unique BA-hour UTC timestamps, matched source A/B/C arithmetic, original CSV SHA256, frozen three weights SHA256 and all `geometry_approved=false`, `model_training_permitted=false`, `population_is_customer_weights=false` flags. A separate successful audit artifact may be claimed **only when** https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43668226350 reaches completed/success.

At the time this report was initially authored the audit run had not yet finished. No combined artifact is claimed in advance.

## Scientific implications, limits and next decisions

- **AZPS and SRP**: the population-vs-county-area spatial weather support choice materially alters genuine observed temperature, typically raising the population-weighted temperature by several °C in sampled winter and summer source weeks.
- **BPAT and CISO**: opposite C−B seasonal sign means that simply applying a single geographic calibration offset would be physically unjustified.
- The apparent seasonal pattern in weather exposures **does not demonstrate** anthropogenic ALL/NAT causal attribution, temperature-demand causal response, model skill or superior prediction.
- Critically, the three proxies cannot be ranked by accuracy against electrical load from this evidence alone: a BA is an operating function, not necessarily an exclusive administrative map, and the true load-weighted weather estimand requires utility/customer/geographic demand evidence.
- E1 original actual source 2020–2025 six-year panel (210,432 weather BA-hours; 260 EIA-930 original demand gaps; 70 anomaly candidates) remains quarantined from final model training. 2024–2025 formal predictive holdout remains untouched.
- Freeze actual PUDL county source to a stable tagged release before publication because the previous PUDL county input was produced from a mutable `nightly` object.

**Current gate: historical BA geography approved = FALSE; training permitted = FALSE.** C-1 is frozen.
