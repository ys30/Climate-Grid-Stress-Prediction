# C2 E0 → E1: verified episode QA and strict ERA5 join gate

Date: 2026-11-12.

## Verified real-source episode output

Independent GitHub Actions run: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43316280076

**2023 (four BAs):**
- Exactly four **one-hour** blank-demand episodes: AZPS on Dec 19 20:00 UTC and Dec 28 21:00 UTC; CISO on Oct 31 20:00 UTC and Nov 14 19:00 UTC.
- No absent source timestamp keys after previous-year H2 boundary source inclusion.
- **33 candidate quarantine flags**, encompassing high spike observations and their neighboring low-ratio records (not necessarily 33 independent errors); source original records preserved.
- 35,036 numeric source demand BA-hours; 35,003 of them not candidate-quarantined. These are strictly a source-QA status, **not approved full weather-model training rows**.

**2024 (four BAs):**
- CISO Nov 1 07:00 to Nov 3 06:00 UTC: **48 contiguous blank demand hours**.
- SRP Mar 12 07:00 to Mar 13 06:00 UTC: **24 contiguous blank hours**.
- SRP Mar 15 07:00 to Mar 16 06:00 UTC: **24 contiguous blank hours**.
- Other AZPS/BPAT 2024 hourly raw demand available throughout after boundary reconciliation.
- 0 candidates using the defined two-neighbor 2×/0.5× rule. This flag screen is neither a general outlier proof nor a data-cleaning guarantee.
- 35,040 numeric source demand BA-hours after excluding 96 original blanks. No imputation.

These results correct earlier mistaken implication that 2024 CISO/SRP blanks could be an unlocated mixture; source contiguous episodes are now located.

## Strict model-input contract

Implemented `src/c2_weather_join.py` and `tests/test_weather_join.py`:
- Demand-only observed BA-hour input with retained raw demand and explicit quarantine/model-eligibility flags.
- ERA5 temperature exposure input requires `source_dataset=ERA5`, UTC start-hour labels, BA IDs, temperature finite values, and an explicitly documented BA-area or load-weighted gridded-exposure method. **Single-city point weather is rejected.**
- Detect duplicate source keys, refuse timezone-naive hourly labels, and preserve only complete-case join records; no value imputation.
- Output contains timestamp and calendar covariates plus raw-demand/temperature; no model trained in this stage.

**Caveat:** The join contract is implemented, but a BA-area-weighted, grid-cell-vintage documented ERA5 historical source has **not yet been acquired**, so no empirical joint weather–demand panel or held-out prediction result is claimed.

## Next source acquisition requirements
1. Define geographic BA exposure polygons, shapefile/GeoJSON version and weights (uniform area versus empirically derived BA load weights; do not treat BA reporting territory as equal to states by default).
2. Obtain ERA5 hourly 2m temperature for the polygon-grid intersections, with source reference and 0–360 to −180–180 longitude normalization if required.
3. Audit UTC hour alignment, weather coverage and 2020–2025 source overlap; keep dataset access separate from holdout model decisions.
4. Evaluate purely calendrical demand benchmark before supervised weather-response models (only after full input source approval); still no anthropogenic attribution without ALL/NAT climate counterfactual.

Five future climate pathways remain SSP1-1.9/SSP1-2.6/SSP2-4.5/SSP3-7.0/SSP5-8.5, subject to dataset comparability gate.
