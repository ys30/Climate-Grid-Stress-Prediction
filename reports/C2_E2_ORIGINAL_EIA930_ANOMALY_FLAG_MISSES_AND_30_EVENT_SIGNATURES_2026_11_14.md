# C2 E2 — EIA-930 original anomaly screen misses two adjacent SRP hours

Date: 2026-11-14 Mountain (2026-11-15 UTC).
Status: **ACTUAL ARCHIVED SOURCE DIAGNOSTIC; NO CORRECTION, MODEL TRAINING, OR INDEPENDENT REVISION AUTHORIZATION.**

## Evidence and reproducibility
Independent local Python rerun on the successful real 2020–2025 source-panel Actions artifact (run 43629200989, artifact 14127710411, ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`; original 210,432 BA-hours, inner GZIP SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`). The separate source anomaly 70-hour review was obtained from successful run 43646854297, artifact 14134356821 (ZIP SHA256 `7d6f54be5466d1e4a51d095ad2e0b209d4cb15cdd62a3b81e19f8206618372c9`).

Original 70 flagged BA/UTC-hour keys form 30 contiguous flagged clusters: AZPS 7, BPAT 0, CISO 1, SRP 22. 19 clusters span three flagged hours. Across the 30 clusters, 20 have a peak >=3× a local, unflagged six-hour-neighbor median; 8 reach >=10×. These are **source diagnostics, not confirmed errors**.

## New discovery: unflagged extreme hourly values adjacent to flagged source hours
A restricted **secondary sensitivity screen** scanned *unflagged* hours within 6 UTC hours of an original flagged hour, looking for original demand >=3× the median of valid *unflagged* hours within the preceding/following 24 hours (minimum 12 valid reference hours). Exactly **two** newly flagged secondary candidates were found, both SRP:

| UTC interval start | Original demand MW | Local source median MW | Ratio | Originally flagged? |
|---|---:|---:|---:|---|
| 2023-02-27 00:00Z | 45,097 | 3,096 | 14.566 | No |
| 2023-02-27 01:00Z | 27,030 | 3,102 | 8.714 | No |

Actual source-hour sequence:
- SRP 2023-02-26 22:00Z = 2,958 MW (originally flagged)
- 2023-02-26 23:00Z = 68,520 MW (originally flagged)
- 2023-02-27 00:00Z = 45,097 MW (**originally unflagged, secondary candidate**)
- 2023-02-27 01:00Z = 27,030 MW (**originally unflagged, secondary candidate**)
- 2023-02-27 02:00Z = 3,578 MW (originally flagged)

This means original 70 flags / 30 flag clusters are NOT exhaustive anomalous episode counts. Simply masking the original flagged hours would leave at least 45,097 MW in the 2023 SRP validation subset. The secondary search is deliberately local to existing events: **it does not establish there are no further missed events**.

All 30 original clusters had a before-versus-after 24-hour observed-median ratio between 0.8 and 1.2, supporting transient source signatures, NOT independently proving reporting error. Local medians are not a weather-adjusted expected load. No original values were edited, excluded or imputed. Do not tune using 2024–2025 test metrics.

## Scientific decision
Review original EIA-930 source-vintage revisions and BA reporting convention for the expanded SRP episode before declaring data error. Freeze a source-only anomaly rule and explicitly report flag sensitivity. The six-year ERA5 BA exposure still uses historical-unapproved area masks. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE` and `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain BLOCKED. `model_training_permitted=false`. C-1 remains frozen.

Independent complete 30-event signature CSV, secondary two-hour CSV, JSON provenance, methodological report and local Python script were packaged as `C2_E2_ANOMALY_MISSED_FLAGS_AND_EVENT_SIGNATURES_2026-11-14.zip` in the project conversation.
