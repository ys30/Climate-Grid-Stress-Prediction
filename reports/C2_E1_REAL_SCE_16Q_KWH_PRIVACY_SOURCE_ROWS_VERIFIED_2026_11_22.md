# C-2 E1 — real SCE 2020–2023 16-quarter source privacy/kWh profile verified (2026-11-22)

**Real publisher source audit complete. County-level electricity load and BA weather exposure are not yet verified.**

[Authentic quarterly SCE source-row CI run 45043437708](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/45043437708) completed **SUCCESS**; artifact **14762517394**, JSON SHA256
`8f263938f5cca0958f78aa9a0a838d7a45ad8c7557331ff058d46fc1951b616f`.
Re-downloaded all **16/16 exact SCE publisher 2020–2023 XLSX URLs**, checked each against independently published original source SHA256 manifest artifact **14762472124**, run [45043217550](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/45043217550).
Original source rows were parsed, checked by calendar quarter, classified for `Combined` and kWh states and analyzed for duplicate `ZIP,month,class` keys. No original raw publisher data was modified.

## Actual source-cell inventory

| Source measure, 2020–23 | Total observed source rows |
|---|---:|
| SCE original quarterly reported rows | **143,778** |
| `Combined=Y` | **77,149** |
| `Combined=N` | **66,629** |
| Blank reported `TotalkWh` | **93,349** |
| Positive reported `TotalkWh` | **50,413** |
| Negative reported `TotalkWh` | **16** |
| Literal zero reported `TotalkWh` | **0** |
| Additional duplicate ZIP×month×class row count | **105** |

The kWh states reconcile exactly: `93,349 + 50,413 + 16 = 143,778`. The privacy flags reconcile: `77,149 + 66,629 = 143,778`. These are source-row counts, NOT distinct metering accounts, actual unique ZIP loads, county consumption MWh, or physical electricity deliveries. Each group with `Combined=Y` requires utility-specific merged ZIP provenance to interpret geographically.

**SCE 16 negative report rows** are separate from SDG&E's 50 residential negative report rows; do not combine or label them all errors without source codebook. The 105 extra ZIP-month-class records are spread over the first **7 quarters** (2020 Q1 through 2021 Q3), **15 in each**, with zero extra duplicates in the subsequent 9 quarters. The 2020 Q1 exact-original-row audit [44922097300](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44922097300) showed 12 exact blank duplicate groups (four ZIPs × three months) plus 3 `93691` groups with different source values. This prohibits automatic global deduplication and source kWh summation.

## Research methodological restrictions

- SCE source has a 2022 Q2 filename typo (`SCE_2002_Q2...`), but the actual downloaded internal year was verified to be 2022.
- Source workbook headers contain variable newlines (e.g. `Zip\\nCode`); the corrected audit normalizes header whitespace rather than excluding real original quarter files.
- No published donor/recipient ZIP geographic disaggregation was recovered; `Combined=Y` cannot be treated as physically located in the displayed ZIP.
- Literal missing `TotalkWh` is not a metered zero. Negative net electricity might involve self-generation or billing, but no mechanism has been independently proven.
- 2020–2023 SCE and SDG&E reports reflect **utility ZIP-sector aggregate source records**, not a complete historical CISO control-area load footprint or validated hourly temperature-weighted demand.
- PG&E original ZIP source access still requires the original publisher form; no PG&E data is credited as verified.

## Provenance and next steps

`scripts/c2_sce_real_2020_2023_original_quarter_index_audit.py` pins original XLSX schema/hash identities;
`scripts/c2_sce_16q_real_zip_privacy_source_profile.py` rechecks every original SHA and audits row states;
`tests/test_c2_sce_16q_real_zip_privacy_source_profile.py` guards against treating blanks as zero, adding duplicate ZIP rows, and accepting the wrong internal year.

These results are adequate for a data quality and privacy-limits subsection, but NOT for spatial energy-weighted BA weather attribution. Independent utility source privacy aggregation rules, the USPS/HUD time-correct ZIP-to-county correspondence and an actual CISO operational BA footprint still need evidence. `GEO_LOAD_RELEVANCE=BLOCKED`; `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`; `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`; `model_training_permitted=false`. C-1 frozen. 2024–25 EIA-930 hourly demand sealed for model selection.
