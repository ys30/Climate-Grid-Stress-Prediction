# C2 E2: 70 candidate demand-anomaly hours represent 30 contiguous UTC events

Date: 2026-11-14 Mountain / 2026-11-15 UTC.
Status: **OBSERVATIONAL SOURCE TRIAGE ONLY. NOT CONFIRMED DATA ERRORS. E2 TRAINING BLOCKED.**

## Independently reproduced actual archived sources
Two successful original GitHub Actions archives were downloaded and SHA256-verified:
- Full 2020–2025 EIA-930/ERA5 source archive: run 43629200989, artifact 14127710411, ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`.
- Separate 70-hour neighborhood review: run 43646854297, artifact 14134356821, ZIP SHA256 `7d6f54be5466d1e4a51d095ad2e0b209d4cb15cdd62a3b81e19f8206618372c9`.

The 70 BA/UTC timestamps were exactly matched between archived source flags and the independent review. A new Python script clustered consecutive UTC-hour flags within BA only. It did not alter or impute a single original EIA value, use predictive holdout skill to tune thresholds, or fit a model.

| BA | Source-flagged hours | Contiguous UTC flag clusters | Three-hour clusters | Large positive hours | Expanded-neighborhood unremarkable flags |
|---|---:|---:|---:|---:|---:|
| AZPS | 12 | 7 | 2 | 2 | 5 |
| BPAT | 0 | 0 | 0 | 0 | 0 |
| CISO | 1 | 1 | 0 | 0 | 0 |
| SRP | 57 | 22 | 17 | 18 | 36 |
| **TOTAL** | **70** | **30** | **19** | **20** | **41** |

In addition to these 20 large-positive hours, there was one large-negative candidate hour (SRP) and eight moderate candidate hours (AZPS five, CISO one, SRP two).

## Interpretation
The original immediate-neighbor source screen may mark an extreme central hour and its neighbors. Accordingly, **70 source flag hours are not 70 independent physical or reporting error events**. This data-level clustering clarifies the earlier 41 expanded-neighborhood-unremarkable flags; these must not be called error-free, because many are adjacent to an extreme. The SRP 57 flags comprise only 22 contiguous clusters, 17 of which are three-hour clusters.

These are candidate source events, **not 30 confirmed errors or 30 documented grid-stress events**. Revision-vintage independent confirmation is still required before excluding any observation. The original weather exposure candidate geography is not load validated. `model_training_permitted=false`. Keep 2024–2025 sealed, C-1 frozen.

The archived reproducible full 30-event CSV, JSON manifest, report and script were produced as `C2_E2_ANOMALY_30_EVENT_AUDIT.zip` in the conversation. They are separate from GitHub Actions source artifacts.

## Next actions
1. Prioritize the 17 SRP triple-hour clusters for original EIA-930 historical revision cross-check, especially central spikes; test whether neighbors were mechanically flagged.
2. Freeze anomaly rules using source metadata and training-only decisions rather than test-set metrics.
3. Independently verify BA geographic weather exposure; do not treat PUDL county-set match or HIFLD 2018 boundaries as hourly BA load weights.
