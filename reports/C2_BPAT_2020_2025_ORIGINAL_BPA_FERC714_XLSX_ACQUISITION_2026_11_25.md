# C-2 BPAT — Operator-original 2020–2025 BPA FERC-714 acquisition workflow (2026-11-25)

## Independent official original source located

The operator's [official FERC-714 reports index](https://transmission.bpa.gov/business/operations/ferc714/default.aspx) lists six reports for years 2020–2025, with the following directly linked workbook source URLs:

```
https://transmission.bpa.gov/business/operations/ferc714/FERC714_2020_Masterx.xlsx
https://transmission.bpa.gov/business/operations/ferc714/FERC714_2021_Masterx.xlsx
https://transmission.bpa.gov/business/operations/ferc714/FERC714_2022_Masterx.xlsx
https://transmission.bpa.gov/business/operations/ferc714/FERC714_2023_Masterx.xlsx
https://transmission.bpa.gov/business/operations/ferc714/FERC714_2024_Masterx.xlsx
https://transmission.bpa.gov/business/operations/ferc714/FERC714_2025_Masterx.xlsx
```

BPA's official page explicitly describes annual reports including **BA area loads/interconnections, interchange, peak loads, and forecasts**. Those categories **must not be equated automatically** with EIA-930 `type=D` hourly reported demand: differences in jurisdiction, net/gross, native intervals, balancing scope, embedded forecasts or time labels require source-level reconciliation.

## Implemented actual-source GitHub Actions pipeline

- `scripts/c2_bpa_ferc714_original_acquisition.py` downloads each *original* XLSX URL and retains the byte-identical report. It calculates file SHA-256, checks valid ZIP/XLSX workbook structure, collects all sheet names and first 35 rows (up to 22 source cells per row), records original workbook worksheet paths and source URL.
- `tests/test_c2_bpa_ferc714_original_acquisition.py` defines **four synthetic-only tests** for XLSX XML parsing, six-year source manifest, fail-closed bad bytes, and unsupported years.
- `.github/workflows/c2-bpa-ferc714-original-six-year.yml` runs tests and attempts the **real operator download** on push or manual dispatch; artifacts always upload partial evidence and failure diagnostics. No external credentials or user EIA API key is used. All outputs remain `model_training_permitted=false`, `actual_EIA930_source_comparison_completed=false`.

## Execution status, strict provenance

The BPA year links were inspected from the official index. **Direct workbook downloading from this assistant runtime failed** (no connection/name resolution), so no original BPA workbook bytes or verified original SHA values are available here. The GitHub Actions workflow and test files were **successfully committed**, latest workflow commit `fedfc670b6d49d23f7c569769bc0cf50af763e88`. Whether a GitHub Actions runner successfully fetched the workbooks or ran the four tests **was not established** at the time of this report; the run status and artifact must be independently checked. No actual FERC-714 values were extracted or compared against EIA-930.

## Next measured step after original sources exist

Examine workbook inventory, identify the exact respondent BA-year and EIA-930-like annual/hourly load fields, units/timebase, historical reporting amendments, and define an exact comparability crosswalk. Then independently compare BPAT annual peak or annual sum of *matched observed demand*, conditional on identical definitions. Disallow annual peak vs demand-energy sum, scheduled exchange vs reported load, or BA vs customer load comparisons.

This **load source** audit does not by itself establish **historical BA geographic polygons or geolocated hourly load**. EIA-vintage discordance, PUDL county-join service-area limitations, and operational BA geography remain research blockers. No historical model training, climate attribution, SSP/CMIP6 or PyPSA adequacy results. **C-1 frozen.**
