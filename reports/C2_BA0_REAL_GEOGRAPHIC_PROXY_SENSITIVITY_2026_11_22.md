# C-2 BA-0: actual EIA-930 / ERA5 geographic proxy sensitivity (2026-11-22)

This is a **completed descriptive source-data analysis**, not a model or a causal attribution experiment.

## Verified inputs and reproducible user delivery

The SHA-pinned, previously retrieved source-clock diagnostic contains **10,416 EIA demand × ARCO ERA5 hourly rows** for 14 complete BA×months: CISO/BPAT/SRP in Jan/Jul 2023 and Jan/Jul 2025, plus AZPS Jan/Jul 2025. Input paired CSV SHA-256: `e754b35f2c6aaeb80b2a932cc9885382d3a1a93ae0d59cc27077810e65bbeb5c`. Every included BA×month has 744 unique exact UTC hourly rows. AZPS 2023 is excluded due to two authentic negative source demand values and failed **strict annual source gate**, not weather missingness.

The complete local delivery `C2_BA0_Geographic_Proxy_Sensitivity_2026_11_22.zip` contains `analyze_proxy_sensitivity.py`, 14 BA×month quantitative output rows, SHA manifest, scientific report, two locally passing contract tests, and a copy of the source-clock-paired CSV. ZIP SHA-256: `40feadcee464856eddd374a4ca8c2a2c964d2f23389b1ffe288e7ae7d7ef0799`. The raw EIA/ERA5 source artifact ZIPs remain in the earlier `C2_BA0_Real_EIA930_ERA5_4Month_Source_Audit_2026-11-22.zip`, not uploaded into this public GitHub repository.

## Actual proxy sensitivity

Candidate B (2024 TIGER county proxy) minus candidate A (2018 HIFLD candidate) area-mean 2m ERA5 temperature; **neither is an approved BA operational load-weighted exposure**.

| BA | Month | Mean B−A °C | Hours A >35°C | Hours B >35°C |
|---|---|---:|---:|---:|
| CISO | 2023-07 | -0.2895 | 38 | 31 |
| BPAT | 2023-07 | -0.1949 | 0 | 0 |
| SRP | 2023-07 | -1.8072 | 472 | 373 |
| AZPS | 2025-07 | -1.3763 | 135 | 79 |
| SRP | 2025-07 | -1.9487 | 326 | 222 |
| CISO | 2025-07 | -0.1704 | 0 | 0 |

Full 14-month table includes median, 5th/95th-percentile signed differences, absolute differences, 30°C and 35°C exceedance counts, source demand mean, and **raw, unadjusted** demand–temperature correlations for each proxy. The raw demand-temperature correlations (e.g., BPAT 2023-07: +0.8981/+0.9003, CISO 2023-07: +0.6415/+0.6433) are descriptive confounded statistics, **not** regressions, fitted forecast skill, causal effects or tests of whether A or B represents BA geography more accurately.

## Methodology and interpretation safeguards

- The output relies on previously authenticated 2023/2025 EIA source and real ERA5 A/B artifacts, not synthetic meteorology. Strict input flags `geography_approved=false`, `model_training_permitted=false`.
- Both candidate temperature proxies use the same meteorological source but different geographic weights, so differences are **geographic support sensitivity**, not distinct weather scenarios or anthropogenic warming.
- 35°C and 30°C are illustrative fixed numerical thresholds, not calibrated system stress thresholds.
- 2025 **was descriptively inspected**, including correlations of 2025 demand and temperature; do not call it a wholly *unseen* holdout. A future preregistered leakage-resistant test and disclosure of the exploration are required.
- No statistical significance or uncertainty intervals, out-of-year fitted model comparison, counterfactual forcing attribution, CMIP6 projections, or PyPSA adequacy results are claimed. Four isolated source months are insufficient for robust annual validation. C-1 frozen and unchanged.

Next empirical step: source-verified full-year weather panel, independently validated BA operational geography / weighting, and explicit preregistered forecast evaluation protocol.
