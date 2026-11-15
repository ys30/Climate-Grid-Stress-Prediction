# C-2: independently validated 384 source ERA5 A/B/C spatial exposure comparisons

Date: 2026-11-14 Mountain. **Source comparison complete; E2 model training BLOCKED; C-1 remains frozen.**

## Verified source
The original successful GitHub Actions run [43666836001](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43666836001), artifact 14143156157, was downloaded and independently SHA256-verified: `6510fef8e749a044c0ccc874a53db8afb671dd923f8269283d077562c5002598`. Source contains exactly 384 distinct BA-hours (AZPS, BPAT, CISO and SRP, each complete 24-hour UTC days 2023 Jan 15, Jul 1; 2025 Jan 15, Jul 1). Independent source-level recalculation verified all hourly A/B/C temperature differences to 2.1e-6 °C and upstream four-BA 96-hour means.

A = area-weighted 2018 HIFLD candidate; B = area-weighted TIGER 2024 county candidate; C = Census 2020 estimates-base population-weighted county candidate. **None** is certified for historical BA load exposure.

| BA | Mean B−A °C | Mean C−B °C | Mean C−A °C | C > B |
|---|---:|---:|---:|---:|
| AZPS | −1.921391 | +4.814620 | +2.893228 | 96/96 hours |
| BPAT | +0.006933 | +0.595046 | +0.601979 | 48/96 hours |
| CISO | −0.277619 | +0.390574 | +0.112955 | 48/96 hours |
| SRP | −1.930985 | +1.964409 | +0.033425 | 96/96 hours |

The independent 16 BA-day table reveals seasonal sign reversal of C−B in BPAT and CISO: BPAT +3.042953 °C (2023 Jan 15) versus −2.525677 °C (2023 Jul 1); CISO +3.045461 °C versus −2.050496 °C on the same days. Both B and C are county-based, and these differences isolate population-weighting sensitivity holding underlying ERA5 data and sample time constant.

These four specifically selected days cannot establish full six-year climatological differences, BA load exposure accuracy, independent-sample p-values, demand model predictive skill or anthropogenic causation. Population weights are NOT customer-load weights. The geography and load quality/holdout gates stay blocked and `model_training_permitted=false`. Keep 2024–2025 demand holdout unopened for modeling.

Reproduction package `C2_ABC_96H_SPATIAL_SENSITIVITY_VERIFIED_20261114.zip` in the project conversation contains 384 verified records, 16 BA-day summaries, source SHA256 manifest, report and Python QA. EIA-930 SRP February 2023 independent-vintage revision verification is still not completed. EIA provides per-BA XLSX, six-month CSV, and API sources suitable for source-vintage comparisons.
