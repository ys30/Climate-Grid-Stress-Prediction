# C-2 E1 — actual SCE 16-quarter source recovered and source duplicate keys classified (2026-11-22)

**New real-source CI success. No electric load exposure weights or county meter estimates. C-1 frozen.**

## 2020–2023 SCE original quarterly XLSX verification

The [SCE historical original-source workflow run 45043217550](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/45043217550) completed **SUCCESS**; artifact **14762472124** was downloaded and independently opened. Its original artifact JSON SHA256 is
`90611f178db3b7c96a39dc76c7e9ef721ce349d12391dd24da3e3ebe8b9e598b`.

**16/16 real SCE quarterly publisher XLSX files** were downloaded and checked for real XLSX structure, source SHA256, original field headers and internal year samples. The 2022 Q2 official href contains a `2002` file name typo but **the file's internal observed year was verified as 2022**. Year- and period-specific original hashes/source URLs were preserved in the workflow JSON. The fix was simply to normalize header line breaks and spaces (e.g. `Zip\\nCode` vs `Zip Code`) in recognition; missing original source data were not fabricated. Only publisher original *source structure* and sampled internal year were admitted. Full 16-quarter retail kWh sums, all rows' privacy semantics, and reconciliation to EIA-861 annual MWh have NOT been validated by this workflow.

SDG&E actual original 16-quarter CSV+publisher SHA512 were already verified independently by successful [run 44922065108](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44922065108): **27,504 rows**, 50 negative reported residential kWh records and substantial privacy merging. **The source availability and schema audit now covers 32 SCE+SDG&E quarterly files, not 32 quarters of county MWh.**

## SCE exact original 2020 Q1 duplicate finding

Separate authentic original-SHA-pinned SCE raw Excel duplicate run [44922097300](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44922097300) completed **SUCCESS**, artifact **14715070412**, JSON SHA256 `d06865243dcdf97ff634cb97713f7494b41c29a286f6a0f858bd7762e5d8bf6f`.

There are **9,324 original 2020Q1 data records**, **9,309 unique ZIP×month×customer-class keys** and **15 repeated-key groups / 15 extra rows**. The exact original raw Excel row numbers were recovered.

- ZIPs `93634`, `93643`, `93664`, `93670`: 4 ZIPs × 3 months = **12 groups** with truly identical paired raw source values, `Combined=Y`, all kWh/account/average cells blank.
- ZIP `93691`: January, February, March = **3 groups** with **nonidentical paired source rows**, `Combined=Y`, some kWh/account source entries not blank.
- **Do not mechanically deduplicate all 15 groups** or sum 93691 pairs: their physical privacy group behavior is not yet source-explained.

The exact original source audit intentionally keeps `source_aggregation_permitted=false`.

## Next real science gate

1. Extend source-only SCE 16-quarter privacy flags, blank/positive/negative kWh, repeated keys, original denominators and all-rows year/period QA; do not infer county MWh.
2. Locate publisher descriptions of donor/recipient ZIP privacy-group mechanisms, and independent year-specific USPS/HUD ZIP→county correspondence. ZIP geographies may cross counties.
3. PG&E remains non-verified because original public download requires a form; do not treat landing-page HTML as electricity ZIP source.
4. Crosswalk CISO operating BA and utility reporting scope independently of these electricity sales records.
5. Continue `model_training_permitted=false`, `GEO_LOAD_RELEVANCE=BLOCKED`, `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`. 2024–25 demand holdout not used for model selection. C-1 untouched.

Scripts:
`scripts/c2_sce_real_2020_2023_original_quarter_index_audit.py` and
`scripts/c2_sce_2020q1_exact_duplicate_raw_row_probe.py`.
