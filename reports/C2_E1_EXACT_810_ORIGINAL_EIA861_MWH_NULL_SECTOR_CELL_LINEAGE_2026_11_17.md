# C-2 E1 — Exact raw-cell lineage for all 810 original EIA861 null sales-MWh records, 2020–2023 (2026-11-17)

## Verified source and matching process

All 810 selected PUDL v2026.10.0 long-format null-`sales_mwh` class records for 2020–2023 (four BA: AZPS, BPAT, CISO, SRP) were joined to 468 uniquely identified, original **Sales_Ult_Cust_<year>.xlsx / States / Part A / Bundled / Data Type O** Excel rows. These raw rows were previously verified with their original SHA-256 signature and Excel row location. Original Zenodo archive DOI `10.5281/zenodo.23241340`, with annual ZIP MD5 checks.

**New exact original source header evidence**: successful [GitHub Actions run 44217458692](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44217458692), artifact `14388378072`; original header CSV SHA256 `11ec32b75414a443048d4045e8dbfa56e843dae76db9b362641c811bd67f9b94`. Every 2020–2023 original Sales workbook includes only:
- Excel columns **10–12**: RESIDENTIAL Revenues (thousand USD), Sales (Megawatthours), Customers;
- **13–15**: COMMERCIAL triple;
- **16–18**: INDUSTRIAL triple;
- **19–21**: TRANSPORTATION triple;
- **22–24**: TOTAL triple.

There is **no 'OTHER' source reporting column** for these years. The fifth triple is TOTAL, *not* Other. This directly explains why all 468 relevant original filing groups have a long-format `customer_class=other` null slot even though the original worksheet does not have that field.

## Exact original-cell results

| Source mechanism | 2020 | 2021 | 2022 | 2023 | 2020–23 total |
|---|---:|---:|---:|---:|---:|
| Processed Other slot absent from original form | 116 | 113 | 116 | 123 | **468** |
| Other class-sector MWh original `.` | 84 | 71 | 79 | 108 | **342** |
| **Total processed null cells reconciled** | **200** | **184** | **195** | **231** | **810** |

Breakdown of the 342 original literal-dot MWh Sales cells: **Transportation 235, Industrial 65, Residential 27, Commercial 15**. Of those 342, **340** have literal dot for all three corresponding cells; the other **2** have original revenue `0` but sales MWh and customers `.`, both in 2020 BPAT–WA Transportation: utility 7548 original row 493, utility 14324 original row 981.

By BA, absent original Other + literal original MWh `.`:
AZPS 51+27=78; BPAT 258+214=472; CISO 138+95=233; SRP 21+6=27.

These are exact raw-cell-source classifications, **NOT a measured amount of missing MWh**. `.` is missing notation, NEVER automatically zero, and even a nonexistent category cell does not establish how much electricity was consumed or whether all required electricity sales were reported.

## Reproducibility

- Prior unique source row artifact from [GitHub Action run 44215715006](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44215715006), SHA256 `eda59eaa015fd0cf4eaedb73cb73bda06a1c1fd13d6ba7e72adbd249c8b0ba91`.
- Original source candidates from [run 44051874799](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44051874799), sha `1527647b41c22e1e80b9bfd997276fd3c63b9a73b27924439e739f6cd5caf415`.
- Processed null source 1321-row inventory sha `6e1e43eeec3b6f0bfb73b5eb25241b8d3e5a3fbf4acdfb9485800fa923bc6300`.
- Exact raw header source sha `11ec32b75414a443048d4045e8dbfa56e843dae76db9b362641c811bd67f9b94`.
- **Independent local 810-row exact-cell verification completed**, outputs downloadable as `C2_E1_810_RAW_EIA861_SALES_CELL_LINEAGE_20261117.zip`.
- Fully fail-closed GitHub code: `src/c2_e1_exact_original_810_null_sales_cell_lineage.py`, workflow `.github/workflows/e1-810-original-sales-cells-verified.yml`. [Run 44217883298](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44217883298) was **queued at report composition**, so do not claim an independently completed CI result until checked.

## Independent GitHub result verified after original report

The exact pinned-source reconciliation [GitHub Actions run 44217883298](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44217883298) completed **SUCCESS**, artifact **14388759429**. Downloaded output `C2_E1_810_ORIGINAL_SALES_CELL_LINEAGE.csv` SHA256 **`28069f30f45d9685625e3688146662b7c57d736879c7d4ff2acb363f3ab1a0b2`**. Original confirmed categories were again exactly **468 Other absent raw column**, **342 original Sales cell `.`**, four-year details unchanged.

An independent local merge against the earlier separately built 810-record audit confirmed **810/810** matched unique original row SHA256 values; all **342/342** raw source records with a real sector field matched their original Sales / Revenue / Customers cell values across both independent implementations. The 468 `other` rows differed only in the descriptive missing-column label (`NO_COLUMN` vs `NO_ORIGINAL_COLUMN`), not their original source row signatures or category interpretation.

## Scope and admission

This closes *training/validation-period null-MWh original raw-cell provenance* at the sector-class field level. It does NOT close completeness of actual retail MWh, utility-to-county allocation, historical BA footprint / meteorological exposure, or the independent load-quality/holdout gate. Keep `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL` BLOCKED; `model_training_permitted=false`. C-1 frozen; no sealed 2024–2025 EIA930 hourly demand used.
