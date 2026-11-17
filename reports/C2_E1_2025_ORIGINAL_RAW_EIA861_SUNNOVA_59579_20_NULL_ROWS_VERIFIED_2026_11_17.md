# C-2 E1 — First verified original EIA-861 wide filing: Sunnova 2025 anomalous 20 long-format null rows (2026-11-17)

## Original raw upstream release confirmed and downloaded

The **exact upstream raw DOI pinned by PUDL v2026.10.0's `src/pudl/package_data/settings/zenodo_dois.yml`** is **`10.5281/zenodo.23241340`**, NOT a newer mutable EIA version. Official [Zenodo record](https://zenodo.org/records/23241340) version 17.0.0 identifies **`eia861-2025.zip`** MD5 **`dff89c8f144a4497057ff7dad93e1944`**, size 4.8 MB.

Actual [GitHub Actions run 44048424275](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44048424275) completed **successfully**, artifact **14312571915**, with genuine original Excel workbook inspections. The verified downloaded raw ZIP SHA256 was **`f59f6c732bf685fe0a1591b32227f5ce572dc0dfd26bb5caaeed128ac4e3a396`**. Inspected 60 sheets across Excel workbooks; found 150 original rows mentioning target utility **59579** among their leading fields, 82 within sales-named source workbook sheets.

## **20 previously unresolved long records are now traced to FOUR original, unambiguously verified wide rows**

Original source Excel workbook: **`Sales_Ult_Cust_2025.xlsx`**, sheet **`States`**. It lists `Utility Number=59579`, `Utility Name=Sunnova`, `Part=A`, `Service Type=Bundled`, `Data Type=O` (Observed), `Ownership=Behind the Meter`. Verified original rows:

| Raw Excel row number | State | BA | All 15 original sector revenue/sales/customer cells |
|---:|---|---|---|
| **2006** | AZ | AZPS | literal `.` in every cell |
| **2008** | AZ | SRP | literal `.` in every cell |
| **2011** | CA | CISO | literal `.` in every cell |
| **2078** | UT | BPAT | literal `.` in every cell |

Each source wide row contains **five** class sectors × **three** measures (revenue, MWh sales, customers) = **15 literal dots**: **60 literal dots across the four rows**. The exact four source rows and original field values were independently verified against the downloaded original-source artifact, not inferred from PUDL's processed output. Original row-level CSV source hash: `f8036da6ecf75feab3e97dfefde463d9e5b84d3364e9018a045a623010b348cb`.

This directly explains the **20** processed PUDL null-MWh long-format slots without positive sibling category sales found previously (one per sector in each of four source filings). It confirms **source-level missing notation**, NOT a numerical zero or absence of all underlying commercial activities. This also reveals that utility 59579 is **Sunnova, with original reporting ownership/business designation "Behind the Meter"**, suggesting special caution against equating its annual reporting cells to conventional retail-hourly BA demand.

Important: previous **1,301** additional null-MWh rows have positive sibling category sales in the long table but have **not all been individually traced to original annual workbooks**. Only these four original filing groups / 20 null rows received direct raw-Excel validation this turn.

## Quality and reproducibility

- Workflow source: `src/c2_e1_raw_2025_eia861_utility_59579_audit.py` commit `e621f33d6385c58713588508ae5b4ce496614e47`.
- Workflow: `.github/workflows/e1-raw-2025-eia861-59579-source-audit.yml` commit `d985c1e539a5890dee9a1973e2fc7cc1da57bf74`.
- Standalone locally verified result: `C2_4_VERIFIED_ORIGINAL_2025_EIA861_SUNNOVA_FILINGS.csv`, published separately in the reproducibility bundle, alongside `PROVENANCE.json`.
- Python tests `tests/test_c2_e1_raw_2025_eia861_utility_59579_audit.py` verify pinned archive mismatch fails closed, original Excel row extraction operates, and does not mislabel original NA as proven structural zero.

## Scientific admission unchanged

This is **original source-cell validation** for 20 particular null category slots; it is NOT validation of historical BA polygons, customer county assignments, annual sales for every missing source row, spatial weights, or hourly operational EIA-930 demand. Do **not** treat `.` as numeric `0` without source rules. The named quality gates `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain unapproved; `model_training_permitted=false`. 2024–2025 *hourly demand test* records remain sealed; only public 2025 annual EIA-861 source data were read. C-1 remains frozen.

### Next scientific priority
Trace a representative, stratified set of 2020–2023 **1,301 positive-sibling category null rows** to raw workbooks using this pinned DOI (plus year-specific file MD5) and test whether raw `.` or blanks match the processed null slots. Only after that tackle utility–county **load relevance** with actual spatial allocation evidence, not population proxy alone.
