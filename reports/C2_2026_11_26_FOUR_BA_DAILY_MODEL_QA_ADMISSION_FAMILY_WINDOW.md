# C-2 — real four BA anomaly-family daily-model admission sensitivity (2026-11-26)

## This turn: executed, not hypothesized

On the verified 210,432-hour original-source EIA930 × candidate ERA5 archive, re-estimated the previously specified descriptive daily-peak cold/warm hinge model on full 24h UTC days. Referenced the independently screened 23-hour source QA candidate ledger; fixed **four** model sensitivity scenarios: (1) all original complete days; (2) omit original source-flagged UTC dates; (3) omit flagged dates plus unflagged spike-family candidate dates; (4) omit that union plus ±1 UTC day. No original values are edited, reclassified or discarded in primary output.

The original flagged family is broader than the additional candidate list. **Three newly unflagged screened hours occur on only two dates**: AZPS 2024-01-23 and SRP 2023-02-27. SRP 2023-02-27 already contains a source-flagged observation (although its very high 00:00 and 01:00 hours are unflagged); thus at **daily** aggregation adding the unflagged SRP hours does **not** exclude further dates. AZPS 2024-01-23 is the sole new excluded UTC date in this comparison.

| BA season | Original full-source cold hinge (MW/°C) | Exclude source-flagged dates | Plus unflagged candidate dates |
|---|---:|---:|---:|
| AZPS winter | 21.02 | 69.00 | **73.77** |
| AZPS nonwinter | -147.80 | -142.99 | -142.99 |
| BPAT winter | 184.99 | 184.99 | 184.99 |
| BPAT nonwinter | 50.27 | 50.27 | 50.27 |
| CISO winter | 194.67 | 194.67 | 194.67 |
| CISO nonwinter | -550.45 | -549.99 | -549.99 |
| SRP winter | 35.47 | 52.65 | **52.65** |
| SRP nonwinter | -175.67 | -162.37 | -162.37 |

AZPS winter daily-peak RMSE changed from ~3,232.90 MW on original to ~438.07 MW on source-flag-day sensitivity and **371.40 MW** after adding the newly flagged-independent AZPS day. These are high-leverage source-data diagnostics, **not approved error removal**. BPAT 2020 unflagged 11,742 MW hourly excursion is below the intentionally strict 3× candidate screen; it remains pending independent review.

Reproducible downloadable local output `C2_Four_BA_Review_Family_Daily_Admission_20261126.zip` contains executed local script, full 32-row model sensitivity, candidate UTC date ledger, differential CSV, source module, provenance, logs, and **6/6 actually passed local tests**. The local ZIP SHA-256 is `2d4b017c702b499c712aace1f6566e759ba3d6f7a0de25b3b609d51b41124939`; archive CRC passed. Original 2020–25 source zip is separately archived; it is not included here.

## Scientific decision and next actual data gate

The earlier unflagged SRP spike records must be reviewed as **hourly source events**, but **do not create additional complete UTC day exclusions** once all source-flagged dates are excluded. Blindly reporting 3 unflagged hours as 3 new excluded modeling dates would be wrong. AZPS 2024-01-23 is the newly consequential extra review date.

The model remains descriptive, candidate historic BA ERA5 masks are not operator certified, EIA930 API year gaps for AZPS/BPAT 2020 persist, and no causal, model-training, or future SSP/PyPSA claims are admissible. **C-1 frozen.**
