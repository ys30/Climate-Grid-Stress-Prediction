# C2 E1 — ACTUAL original EIA861 2020–2023 annual source-candidate audit (2026-11-17)

## Actual reproducible upstream and successful CI

Original source is the PUDL v2026.10.0 tagged raw archive **Zenodo DOI 10.5281/zenodo.23241340**, original archived annual source ZIPs for 2020–2023 with four explicit independently verified MD5 hashes:
- 2020 `ef71e150dd76b2fbce8504ce7159358e`
- 2021 `c088fae5dca1c1c38a11094a2a096735`
- 2022 `8a88824bec4b2aecdc04b0b62fa41452`
- 2023 `7472a6617cc00ff4ae10440f7ef12805`

Successful original Excel source download/scan **[GitHub Actions 44051874799](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44051874799)**, artifact **14313717508**, independently downloaded, unpacked, re-counted and confirmed by a separate Python container read. Full C2 phase-1 [CI run 44051874797](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44051874797) **success**.

The pinned processed prior source is verified artifact 14312002877, internal `C2_E1_MISSING_MWH_SAME_FILING_1321_ROWS.csv` SHA256 `6e1e43eeec3b6f0bfb73b5eb25241b8d3e5a3fbf4acdfb9485800fa923bc6300`. It provides 810 null-MWh source category rows in the locked 2020–23 training/validation interval.

## New actual original-data measurements

| Source year | Processed missing MWh-class rows | Unique year–utility–state–BA groups | Groups with original Sales workbook candidates | Groups with exactly one candidate | Groups with multiple candidates | Original candidate Excel rows | Candidate rows with ≥1 literal dot |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 200 | 116 | 116 | 105 | 11 | 137 | 62 |
| 2021 | 184 | 113 | 113 | 102 | 11 | 134 | 54 |
| 2022 | 195 | 116 | 116 | 104 | 12 | 131 | 59 |
| 2023 | 231 | 123 | 123 | 108 | 15 | 159 | 71 |
| **Total** | **810** | **468** | **468** | **419** | **49** | **561** | **246** |

**468/468** distinct derived utility–state–BA–year groups found ≥1 candidate original Sales workbook row containing the exact utility ID in an early column and exact BA/state labels. 419 had exactly one candidate; **49 had multiple candidates**, including two groups with nine candidates and one with 18.

This is successful **source candidate provenance**, not one-to-one original-cell lineage. For some groups, original Excel includes separate workbooks `Sales_Ult_Cust_YYYY.xlsx` and `Sales_Ult_Cust_CS_YYYY.xlsx`; do not collapse their rows into one report without comparing original Part, Service Type, Data Type and business model.

Original candidate row contents are preserved, with workbook name, sheet, Excel row, exact cell values, source signature SHA256, literal `.` count. The fact that **315 of 561** candidate rows have no literal dot is not evidence of zero demand or source mismatch: missing modern sector slots may be caused by absent wide columns, blank cells or the detailed ETL pathway. Actual raw column mapping must precede per-class conclusions.

## Scientific implications

This materially strengthens source provenance for the entire training/validation interval beyond the already completed four Sunnova 2025 raw filings; no actual 2020–23 class-specific cells are yet verified as structural or nonapplicable for all 810 nulls. The next decisive validation must map each raw workbook's **year-specific header/sector labels and numeric triples** (revenue, MWh, customers) to each long `customer_class` and resolve source candidate ambiguity for the 49 multi-candidate keys. The raw long-format transform tag explicitly executes `stack(level=0,dropna=False)`, so candidate existence does not certify that a null class had positive or zero electricity sales.

**Do not count 810 processed null rows as 810 missing positive MWh**, infer a total omitted MWh value or adjust existing observed annual retail source-coverage percentages from candidate counts. A separate `GEO_LOAD_RELEVANCE` gate still requires defensible customer or meter location allocation across counties; matching original annual Sales is insufficient.

Repository additions: `src/c2_e1_2020_2023_original_sales_candidate_lineage.py`, `.github/workflows/e1-original-2020-2023-eia861-lineage.yml`. Independently verified full output bundle `C2_E1_ORIGINAL_2020_2023_CANDIDATE_SOURCE_AUDIT_20261117.zip` SHA256 `21f97a3d3f001445ae7d100451a69a884383fa9e97026e7edd6c761e6aa1b55c`.

Safety: C-1 remains frozen. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain blocked; `model_training_permitted=false`. No sealed 2024–2025 EIA-930 hourly demand tests opened.
