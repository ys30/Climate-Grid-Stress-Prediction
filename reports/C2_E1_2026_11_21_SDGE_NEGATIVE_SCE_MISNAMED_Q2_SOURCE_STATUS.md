# C-2 E1 — 2026-11-21 verified SDG&E negative load cells and SCE index recovery

## Verified progress

Successfully repaired source code that had stored literal `\\n` tokens in the SDG&E
16-quarter negative-data classifier; original publisher SHA-512 and strict
2020–2023 period checks remain enabled. Real GitHub Actions
[44922065108](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44922065108)
completed **successfully**. Original artifact **14713863065** was
downloaded and independently parsed: **27,504 original quarterly public ZIP
records**, 20,394 zero kWh source cells, 7,060 positive and 50 negative.
All negative observations are `CustomerClass=R`: 28 `Combined=N`, 22
`Combined=Y`. Actual per-period negative counts: 2022 Q2=18;
2022 Q3=4; 2023 Q1=1; 2023 Q2=27. Causes are **not identified**.

## Exact SCE 2022 Q2 publisher-link correction

Original SCE
[Quarterly Customer Data Reports](https://www.sce.com/regulatory/regulatory-information/energy-data-reports-compliances)
lists quarterly data for 2020–2023. Under **2022 / 2nd Quarter**,
the actual linked filename is unusually
`SCE_2002_Q2_ElectricUsageByZip.xlsx` (2002 in filename, 2022 on
the official list), at the source link
https://www.sce.com/sites/default/files/custom-files/Web%20files/SCE_2002_Q2_ElectricUsageByZip.xlsx .
This is a **publisher filename discrepancy** and not independent
proof of workbook observation year. Our source collector now admits
this *one exact official href* with mandatory validation of the
downloaded Excel's internal 2022 year cells. Do NOT simply rename
it to a 2022 file without checking its original source contents.

The official-index workflow
[44922197688](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44922197688)
was **queued when this report was written**: no claim that its 16
quarter source XLSX files have passed.
SCE original Q1 duplicate raw-row check
[44922097300](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44922097300)
also remained **queued**. Its first historical attempt
44919918078 failed due original SCE header normalization;
the revised probe normalizes whitespace but still checks
the exact expected source field names.

## Scientific boundaries

Reported residential negative `TotalkWh` is not necessarily invalid
or comparable with EIA930 BA hourly demand; a net-metering hypothesis
requires original utility definition and independent review.
`Combined=Y` cannot establish physical electricity's ZIP or county.
Observed EIA861 annual retail MWh and the PUDL source support constraints
remain distinct from these SCE/SDG&E public ZIP-month records.

`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`,
`GEO_LOAD_RELEVANCE=BLOCKED`,
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`,
`model_training_permitted=false`.
2024–25 EIA930 demand test not used to tune; C-1 frozen.
