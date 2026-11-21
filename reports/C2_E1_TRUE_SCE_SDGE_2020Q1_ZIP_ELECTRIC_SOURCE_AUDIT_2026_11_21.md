# C-2 E1: REAL 2020 Q1 SCE and SDG&E ZIP-level electricity sources independently verified (2026-11-21)

**Actual source verification completed via GitHub Actions run [44917907054](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44917907054), SUCCESS; published source metadata artifact 14712019950.** This is utility-reported source verification, **NOT county-identified load MWh or a weather-demand model**.

## Source results, not guesses from public portals

| Utility | Publisher original | Original response bytes | SHA256 of real response | Integrity status |
|---|---|---:|---|---|
| SDG&E | [SDGE-ELEC-2020-Q1.csv](https://energydata.sdge.com/downloadEnergyUsageFile?name=SDGE-ELEC-2020-Q1.csv) | 47,681 | `350a0f8e9610dc4347f1705cfeb1ccf06ce1fc4ea528e8f5b88c49cc32b550e7` | **Original CSV VERIFIED**; independently matched original publisher SHA512 hash sidecar |
| SCE | [SCE_2020_Q1_ElectricUsageByZip.xlsx](https://www.sce.com/sites/default/files/inline-files/SCE_2020_Q1_ElectricUsageByZip.xlsx) | 408,525 | `0d814db6abdb342171899eb57201cb3d3c62767b48cb2ce89aec537e2342431b` | **Original XLSX VERIFIED**, workbook and first 18 rows inspected |
| PG&E | [PGE_2020_Q1_ElectricUsageByZip.zip](https://pge-energydatarequest.com/public_datasets/download?file=PGE_2020_Q1_ElectricUsageByZip.zip&type=electric) | 58,299 | response hash varies per download | **NOT VERIFIED**: endpoint returns an HTML page (not original ZIP) despite HTTP success |

**Do not count the PG&E HTML response as electricity source data.** The 2020 Q1 report is listed in PG&E's public portal, but the direct archive endpoint requires further discovery of the actual file-transfer mechanism. Local container direct attempts failed at DNS resolution; GitHub Actions downloaded a 58 KB HTML response instead of the expected ZIP.

## SDG&E real observations

Original CSV fields:
`ZipCode,Month,Year,CustomerClass,Combined,TotalCustomers,TotalkWh,AveragekWh`.

- **1,719 source records**, exactly **573 rows each** for January, February and March 2020.
- Original class row counts: **A 432**, **C 429**, **I 429**, **R 429**.
- **1,421 rows** labeled `Combined=Y`; **298** labeled `Combined=N`.
- **543 rows** have positive source `TotalkWh`.
- The original SDG&E SHA512 hash sidecar (from the same publisher) was read and independently compared to the actual downloaded CSV; **exact match**:
  `a877c771fa7c8804e0e03b30248c11e7eedb8595aa7338cb33327441db713873380c1e4e2f7bdc5eb6273944c1efd2b7189e75113925a`.

The `Combined=Y` prevalence is not itself the number of suppressed MWh or the number of actual merged ZIP service areas. We must inspect whether the raw row's reported zero is a privacy placeholder, a recipient ZIP aggregate or another reporting rule. No county allocation has been performed.

## SCE real observations

Original XLSX workbook first rows were extracted using ZIP/XML:
- worksheet `xl/worksheets/sheet1.xml`; header on row 3:
  `Zip Code, Month, Year, Customer Class, Combined, TotalAccounts, TotalkWh, AveragekWh`.
- A real residential row has ZIP 90001 in Jan 2020, `Combined=N`,
  `TotalAccounts=9842`, `TotalkWh=4044145`, `AveragekWh≈410.91`.
- This confirms a ZIP×month×class reporting grain for SCE's published file; **not** county×actual load measurement.

## Admissibility and next original data task

1. Read actual `Combined=Y` rules from each utility's published data-element dictionaries/privacy decision and inspect source row behavior. Explicitly separate reported zero, structurally merged row and unresolved suppressed activity; never sum multiple donor/recipient ZIP rows as if each contained separately measured load.
2. Extend 2020Q1 source-only audits to **all 16 quarters of 2020–2023**, with SHA pins and per-utility version records; use public original source and reject new format drifts.
3. Obtain time-matched HUD USPS ZIP–county crosswalk (ZIP may span multiple counties), distinguish unique from ambiguous allocations and guard against artificial geographic certainty.
4. Cross-check annual published utility ZIP aggregates with original EIA861 / CEC only after aligning coverage, electric retail service, solar/net metering and privacy suppressions; do not force totals to match.
5. PG&E original 2020Q1 source still requires actual file byte retrieval; no fabricated records from portal HTML.
6. Historical CISO BA membership and 2024–25 demand test remain independently blocked.

**No new estimated county MWh, no model fitting or forecast skill.**
`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`;
`GEO_LOAD_RELEVANCE=BLOCKED`;
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`;
`model_training_permitted=false`; C-1 frozen.

Source-only code `scripts/c2_public_utility_zip_2020q1_source_probe.py`,
regression tests `tests/test_c2_public_utility_zip_2020q1_source_probe.py`,
CI `.github/workflows/c2-public-utility-zip-2020q1-source.yml`.
