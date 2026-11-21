# C-2 E1 public electricity ZIP evidence: real source extraction and restricted interpretation (2026-11-21)

This is an independent research source audit, not C2 E2 model fitting.
**C-1 frozen; 2024–25 hourly EIA930 demand holdout remains sealed for model selection.**

## Actual source milestones already completed

- Original public **SCE** 2020Q1 XLSX SHA256
  `0d814db6abdb342171899eb57201cb3d3c62767b48cb2ce89aec537e2342431b`;
  original **SDG&E** 2020Q1 CSV SHA256
  `350a0f8e9610dc4347f1705cfeb1ccf06ce1fc4ea528e8f5b88c49cc32b550e7`.
- Authentic successful SHA-checked [run 44917907054](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44917907054).
- Fully parsed authentic privacy audit [run 44918996745](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44918996745):
  **SCE 9,324 original rows, 5,055 Combined=Y, 6,161 blank kWh source cells, 15 excess duplicate ZIP×month×class rows; SDG&E 1,719 original rows, 1,421 Combined=Y, 1,176 literal 0 kWh cells.**
- PG&E 2020Q1 access remains form-mediated and direct downloads returned HTML rather than original ZIP; the workflow explicitly does not claim verified PG&E meter data.

## Critical privacy-source interpretation

SDG&E [official public portal](https://energydata.sdge.com/homePage) states that ZIPs not meeting CPUC Decision 14-05-016 privacy requirements are combined with **bordering ZIP codes** before publication. Thus an observed nonnegative usage cell bearing a single ZIP does not necessarily identify consumption physically inside that ZIP. Never read `Combined=Y` 0 kWh as evidence of an unpopulated or zero electricity consumption geographic area.

Independent SCE CPUC testimony likewise describes the 15/15 Rule and combining ZIP energy usage with bordering ZIPs when thresholds are not satisfied:
https://docs.cpuc.ca.gov/PublishedDocs/SupDoc/A2305010/6122/510287358.pdf
(available source; the original SCE quarterly XLSX field semantics have not yet been exhaustively reconciled).

The following are distinct outcomes and should never be silently mixed:
1. Source XLSX/CSV record explicitly reports numeric `0`.
2. Source record contains a genuinely **blank** `TotalkWh`.
3. Source record has `Combined=Y`, including positive reported kWh, but geographic recipient/donor interpretation is not verified.
4. Exact duplicated ZIP×month×class report rows; do not assume that every row corresponds to a distinct recipient group.
5. ZIP legitimately overlaps multiple counties, even for `Combined=N`.
6. Original BA monthly/annual reporting scope may differ from physical utility retail sales and CISO TAC-zone loads.

**No formula setting a ZIP or county load weight proportional to these records is currently scientifically approved.**

## Newly submitted empirical work

- `scripts/c2_sce_2020q1_exact_duplicate_raw_row_probe.py`, authentic original SHA-pinned row numbers and complete seven-dimensional source payload comparison for the **15 SCE extra duplicated keys**, with
  `tests/test_c2_sce_2020q1_exact_duplicate_raw_row_probe.py`, workflow
  [44919918078](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44919918078).
- `scripts/c2_sdge_real_2020_2023_sixteen_quarter_source_audit.py`, reads original public publisher data **2020–2023 16 quarters**, validates individual publisher SHA512 hash sidecars, counts privacy Combined and actual reported kWh states, and requires all 16 original quarters before success. Regression
  `tests/test_c2_sdge_real_2020_2023_sixteen_quarter_source_audit.py`, workflow
  [44920034129](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44920034129).

These two new CI runs were **queued** at this report's initial writing. Their output must be inspected and updated to VERIFIED or FAILED independently. Neither job distributes original utility source data, uploads raw customers, derives county MWh, or modifies frozen C-1.

## Scientific gating and next go/no-go

Only after actual 16-quarter records, independent utility ZIP-mapping rules, and time-matched ZIP–county support are available can a source-only partial-geography analysis begin. Missing public privacy metadata should remain an explicit `NOT_IDENTIFIED` class.

Model geography and load weighting remain blocked:
`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`;
`GEO_LOAD_RELEVANCE=BLOCKED`;
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`;
`model_training_permitted=false`.
