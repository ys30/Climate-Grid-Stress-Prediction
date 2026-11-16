# C-2 research progress checkpoint — 2026-11-15

**Independent reconciliation from archived original-result CSVs; no new climate-demand model results claimed.** C-1 is frozen.

## Confirmed source status

- 2020–2025 source panel: 210,432 BA-hour records, four balancing authorities, 260 source missing hourly demands. 2020–2023 development/validation counts: 140,256 BA-hour records, 140,143 valid demand observations. 2024–2025 70,176-hour model test holdout remains sealed.
- 2020–2023: source-screen anomaly candidates = 68 hours, independently identified additional SRP candidate hours = 2; **70 candidate hours aggregate into 27 contiguous episodes**.
- An independent join of actual event registry CSV and annual source-tail sensitivity CSV verified **16 BA-year original-data groups, 48 scenario/group result rows; 5 BA-years with >=1 original source flag, 11 with zero**. No originally flagged episodes in BPAT or CISO; this does not mean their raw loads are independently validated.
- Event registry: AZPS 7 candidate episodes / 12 hours, SRP 20 episodes / 58 hours; training split 13 episodes / 35 hours, validation 14 episodes / 35 hours. Raw values remain unchanged.
- Real ERA5 spatial A/B/C sensitivity: 384 BA-hour matched observations across four purposively sampled days, but 2018 HIFLD, county-area and population-proxy geometries are not approved BA operational load locations.

## Reproducibility checkpoint
Validated by local Python from previous verified result CSVs, with input file SHA256:
- 27-episode event CSV: `f7a9842f40de7e63482983a238d4384850e194fd3f2cff29e75705c7d9c41b03`.
- 48-row annual-tail sensitivity CSV: `cb793c2ce1af32f0416c1d59a018459b353326b358103be8a01b29a657a6a3df`.
- The earlier standalone SRP two-version comparison prototype's four synthetic unit tests were executed locally again: **4/4 passed**. This is **not** a passing result for the most recent three-version GitHub source/comparison script.

## Scientific gate priorities
1. **P0 Raw EIA-930 vintage cross-comparison**: three pinned historic PUDL ZIPs and comparator exist, but no real comparison artifact was accessible/verified from GitHub Actions. Archive MD5 changes are not proof of SRP source-hour changes. Independent BA reporting-error confirmation remains open.
2. **P0 Geographic load-exposure definition**: 24/24 county membership consistency and 384 real ERA5 samples are source/proxy sensitivity, not independent operational BA load geography verification. Historic BA boundaries and load relevance remain blocked.
3. **P1 Model protocol before fitting**: set 2020–22 temporal train/block CV, 2023 validation, 2024–25 one-time holdout; fixed seasonal/persistence vs GAM vs XGBoost baseline matrix; candidate event quarantine sensitivity **without treating anomalies as confirmed errors**.
4. **P2 Climate impact attribution and scenario grid stress**: ALL vs NAT forcing and SSP climate/PyPSA outputs not yet empirically generated.

## Manuscript readiness
**Data/source quality and sensitivity sections** have real evidence and reproducible diagnostics. **Central model skill, historical attribution and future grid-stress estimates are missing**; submission-ready = **NO**. Repeated QA commits do not imply completion of research hypotheses. `model_training_permitted=false`; C-1 unchanged.

Conversation result bundle `C2_PROGRESS_VERIFIED_CHECKPOINT_20261115.zip` contains 16 BA-year readiness CSV, source-hash JSON, reproducible audit Python and this detailed progress report.
