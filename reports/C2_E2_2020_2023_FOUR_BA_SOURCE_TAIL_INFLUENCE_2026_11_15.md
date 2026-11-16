# C2 E2 — Verified four-BA 2020–2023 original demand extreme-tail influence

Date 2026-11-15. **Source-only diagnostic, not a reporting-error correction or model training. C-1 unchanged.**

## Recomputed archival evidence
- Successful original source run 43629200989; artifact 14127710411; source ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`.
- Original 210,432 BA-hour rows verified, inner compressed CSV SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. **2024–2025 70,176 source BA-hours excluded before any descriptive metrics**, leaving 2020–2023 140,256 BA-hours, of which 140,143 have actual reported demand and 113 are missing.
- 16 BA-year groups, 48 scenario/group outputs, 160 top-ten reported-hour rows. True source anomaly flags and two independently found, previously unflagged SRP Feb 2023 hours were used only for **counterfactual omission sensitivity**, never to rewrite original reported data.

## Scientifically consequential verified examples

| BA/year | Original reported peak MW | Diagnostic peak omitting original flagged hours MW | Peak change | P99.9 change |
|---|---:|---:|---:|---:|
| AZPS 2020 | 101,412 | 7,595 | −92.51% | −0.23% |
| SRP 2022 | 39,298 | 7,629 | −80.59% | −49.24% |
| SRP 2023 | 70,313 | 45,097 | −35.86% | −76.98% |

- **AZPS 2020-01-22 15:00 UTC:** original reported 101,412 MW, adjacent demand 3,446 and 2,270 MW; this is a source-flagged *candidate*, not confirmed error.
- **SRP 2022-06-29 19:00 UTC:** original reported 39,298 MW, adjacent 6,151 and 6,840 MW; original source flag present.
- **SRP 2023-06-03 20:00 UTC:** original annual peak 70,313 MW, adjacent 4,597 and 5,021 MW; original source flag present.

SRP 2023 P99.9 in three *diagnostic* samples: original all valid hours **36,009.149 MW**; exclude 28 originally source-flagged hours **8,289.421 MW**; additionally exclude two unflagged February 2023 candidates **8,240.336 MW**. Corresponding annual peaks are **70,313**, **45,097**, **9,283 MW**. The original source is retained unchanged.

## Interpretation and admission status
These large changes demonstrate source-outlier **metric sensitivity**, not error corrections or causal weather impact. Exclusions change sample cardinality and quantile ranks; all reported quantiles use linear interpolation at `(n−1)p`. Unflagged values may still be anomalous. The extreme SRP/AZPS records require independent historical reporting-vintage verification before categorizing them as errors. In particular a different ZIP checksum alone does not prove a specific EIA demand value was revised.

The full independent 16-BA-year CSV, three scenarios per group, top 10 timestamps per BA-year, SHA256 audit JSON, report and Python reproduction script are packaged in `C2_E2_4BA_2020_2023_TAIL_SENSITIVITY_20261115.zip` (conversation artifact).

Scientific gates still blocked: historical BA operating-area footprint, spatial electricity-load relevance, and original-demand anomaly/holdout admission. The 2024–25 sealed test was not analyzed. `model_training_permitted=false`; do not infer GAM/XGBoost skill, ALL-vs-NAT climate attribution or SSP/PyPSA projected stress.
