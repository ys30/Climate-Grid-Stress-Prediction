# C-2 BA-0 — 325 EIA-930 source-vintage differences: mechanism triage (2026-11-23)

**Executed:** checked the six-year original source ZIP and twelve newer annual EIA-930 source artifact ZIPs (their inner UTC CSV SHA256s agree with original manifests); reexamined exact BA×UTC demand disagreements. This is a **source comparison, not a source revision attribution**.

## What is empirically established

- 325 disagreeing BA×UTC hour keys: 174 numeric value changes, 99 earlier empty/newer numeric, 51 earlier numeric/newer empty, 1 absent newer UTC timestamp. These resolve to **28 contiguous runs** when grouped by BA/year/status.
- **AZPS 2025: 169 changed values** in multiple clusters between 2025-04-30 and 2025-10-22. In 77 of those hours absolute change exceeds 100 MW; in 36 hours exceeds 1000 MW. On 2025-07-31, hourly old/new values differ sharply: 19:00 UTC 6569→0 MW, 21:00 6934→273 MW, 22:00 6929→485 MW. These are verified source-vintage *values*, not yet diagnosed erroneous reporting. On the 169 changed hours, same-clock mean absolute difference is 565.325 MW; shifts of ±1, ±2 and ±24 hours did not improve aggregate MAE over same-clock alignment. This is limited evidence against a *simple global shift*, not a proof against all clock errors.
- **CISO 2024:** old blank 48-hour run 2024-11-01 07:00 UTC to 2024-11-03 06:00; new numeric at all 48.
- **CISO 2025:** old blank 24-hour runs 2025-03-08 08:00 through 03-09 07:00, and 2025-11-01 07:00 through 11-02 06:00; new source numeric at all 48. Proximity to US DST transitions does *not* independently prove timezone-conversion error.
- **BPAT 2021:** later API source has **present UTC keys but blank demand** for an uninterrupted 24 hours 2021-09-15 07:00 through 09-16 06:00. A further blank and numeric disagreement occur on 2021-11-07.
- **BPAT 2023:** later API source has **present UTC keys but blank demand** for 24 hours 2023-10-24 07:00 through 10-25 06:00. Thus these are *source-value omissions, not timestamp omissions*.
- **CISO 2021:** one newer source UTC key actually absent at 2021-11-07 05:00. Other 2021 November 7 discrepancies involve AZPS/BPAT/SRP but need independent HE-label analysis.
- Newer annual files are independently SHA-checked against their downloaded artifacts. **Old combined six-year CSV alone does not establish all original raw hour-ending retrieval bytes**, so it cannot establish whether differences resulted from EIA revisions, extraction dates, time conversion or parsing.

## Next research gate

Retrieve historical extraction scripts/query parameters and, where retained, original source HE CSVs for the changed windows. Compare EIA respondent, type=D, source HE periods, retrieval timestamps, duplicates and null strings *before* UTC conversion; rerun identical date-scope ingestion tests across DST. Preserve both vintages without auto-imputation or replacing one with the other. The existing 2020–2025 weather mask is not an approved operational BA exposure, and no forecast/climate-causal/SSP/PyPSA claims follow from this triage. C-1 stays frozen.

A reproducible user-delivered ZIP `C2_EIA930_325_Conflicts_Mechanism_Audit_2026_11_23.zip` contains 325-row discrepancy table, 28-run summary, lag diagnostic, missing-vs-absent breakdown, report, original ZIP SHA manifest and script. ZIP SHA256: `ed20fb2b32ba95cf3a283f9b9e6a75dfd04595d67688738b7f2d2008b0199119`. Original full source artifacts were previously provided separately; no raw API keys or source ZIP contents were committed here.
