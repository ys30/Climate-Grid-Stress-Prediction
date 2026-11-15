# C2 E2 source-panel readiness: independent 2020–2025 audit

Date: 2026-11-14 Mountain / 2026-11-15 UTC. C-1 frozen. **Original full panel independently checked; E2 model-training gate remains CLOSED.**

## Actual archived evidence
- Successful consolidated source workflow: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989 , artifact 14127710411, archive SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`.
- Inner compressed source panel: `C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz`, SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.
- Previously successful 70-candidate source triage: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43646854297 , artifact 14134356821, archive SHA256 `7d6f54be5466d1e4a51d095ad2e0b209d4cb15cdd62a3b81e19f8206618372c9`.
- Local independent reread validated 210,432 distinct BA-hour source keys and no row-level geography/model admission. Nonmissing source pairs 210,172; missing demand 260; candidate anomaly flags 70. Independent triage had exactly the same 70 BA/timestamp keys. No source alterations or model fits.

## Frozen chronological source split

| Split | Nonmissing source demand-weather pairs | Original demand-null slots | Anomaly candidates |
|---|---:|---:|---:|
| Training (2020–2022) | 105,107 | 109 | 35 |
| Validation (2023) | 35,036 | 4 | 33 |
| Sealed test (2024–2025) | 70,029 | 147 | 2 |
| Total | 210,172 | 260 | 70 |

The 260 source-demand gaps form **28 consecutive BA-specific UTC episodes**, the longest **48 hours** (CISO 2024-11-01 07:00 to 2024-11-03 06:00 inclusive). Thus treating missing hours as independent events is wrong. Some gaps fall near DST transitions, a hypothesis for original timestamp/revision investigation, **not proof** of an erroneous time conversion.

Triage labels from source-verified review: 20 large-positive, 1 large-negative, 8 moderate, 41 without large expanded-neighborhood discontinuity. BA counts: AZPS 12, BPAT 0, CISO 1, SRP 57. These are **unconfirmed flags, not 70 confirmed erroneous observations**.

## Scientific decision
The source panel exists with high hourly coverage; it is NOT a defensible final load-relevant BA weather exposure because the weather weights rely on unapproved 2018 control-area masks. Original source-null slots are preserved and the candidate anomalies are not automatically corrected. The 2024–2025 test window must not be used to choose anomaly thresholds or weather exposure proxies.

Completed E1 administrative PUDL reconciliation (24/24 county sets equal) resolves **source consistency only**, not independent BA operating boundaries or load allocation.

Next: predeclare original EIA-930 revision/event decision rules, independently assess historical BA/weather exposure definitions and 2018 mask sensitivity, and only then admit weather-demand models. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain blocked. `model_training_permitted=false`. No anthropogenic ALL/NAT, SSP or PyPSA stress claim is created by these checks.

Full independently recomputed row-level source inventory, 28 missing episodes, JSON manifests and a Python reproduction script are preserved in the accompanying conversation artifact `C2_E2_SOURCE_READINESS_VERIFIED_2026-11-14.zip`.
