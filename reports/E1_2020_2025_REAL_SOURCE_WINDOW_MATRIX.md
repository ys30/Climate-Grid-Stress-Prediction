# C2 E1 cross-year observed ERA5 × EIA-930 provenance audit (2026-11-13)

## Scope and current verified result
GitHub Actions matrix: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43555573681

Six independent real-data summer-source checks for 2020, 2021, 2022, 2023, 2024 and 2025, each 202X-07-01T00:00:00Z through 202X-07-02T23:00:00Z. Each job fetches preceding-year H2 EIA-930 plus current-year H1/H2 source and a bounded 0.25-degree public ARCO-ERA5 hourly 2m temperature grid; four source BA series AZPS/BPAT/CISO/SRP, exactly 48 source hours per BA.

At document creation **only the 2020 independent matrix job had completed successfully**. The other five remained queued and are **NOT** included in observed-result claims.

### Verified year 2020
- Complete 192/192 source observation pairs (four BAs × 48 UTC hours), using actual public ERA5 and EIA-930 hourly values. All 48 hours per BA present, no imputation, source-quarantine candidate count zero in this sampled window.
- EIA-930 upstream source SHA256: 2019 H2 `5ec5c85be997c6c56bdcf42be3443a4bb6eb0851d704065c11c02eac0d3c48d1`; 2020 H1 `fff83ed20365e69933bdd6ebde06afaa8083930c613363c438844b0fd52034cf`; 2020 H2 `47788a718c26eae5a2453e3471c2b9e7d1a11062a0de70e2dca803163de5a754`.
- Experimental BA-geometry area-weighted ERA5 2m temperature ranges (°C), not formally approved:
  - AZPS 19.182223–33.417975
  - BPAT 8.184143–21.792033
  - CISO 15.452915–29.126351
  - SRP 22.828855–37.016635
- EIA-930 raw MW ranges, same sample: AZPS 2,919–5,573; BPAT 5,054–6,590; CISO 21,844–32,781; SRP 2,789–6,017.

## Six-year reconciliation after CI is complete

`src/c2_crossyear_source_summary.py` and tests provide a fail-closed aggregation: only six distinct years with full 192 each, common archived geometry weights SHA, explicit unapproved geography and zero imputation can produce a six-year source *sample* summary. Expected total **1,152 BA-hour records** (6×2×24×4) is a design target, **not yet six-year verified observed data**.

The six two-day samples must **never** be described as complete ERA5 coverage of 2020–2025 or sufficient to train demand XGBoost/GAM or estimate climate-change attribution.

## Blocking scientific requirements unchanged

Original nationwide HIFLD polygon records carry YEAR=2018 and contain originally invalid source topologies. The source-preserving make_valid sensitivity found a ≈7.08% CISO raw-area diagnostic difference. AZPS/SRP derived polygons share ≈96.66% of the SRP candidate area. All exploratory area weights are barred from the final weather–demand join until separately audited source vintage, topology, overlapping reporting territory and exposure estimand each have documented scientific review.

Actual EIA time-window source comparisons, real ERA5 source access and UTC pairing are technical QA, not authority to use speculative historic boundaries. Train 2020–2022 / validate 2023 / held-out test 2024–2025 remains sealed; no experimental model fitting or SSP future-grid prediction has been performed.
