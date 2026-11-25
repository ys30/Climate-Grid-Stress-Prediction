# C-2 BPAT — Real six-year EIA-930 observed-demand comparison baseline (2026-11-25)

## What was actually computed

Reopened the **original actual 72-month six-year EIA-930/ERA5 archive** `C2_2020_2025_72_Month_Original_Source_Archive.zip`, verified its inner archived demand/weather gzip SHA against original source manifest, selected all **52,608 BPAT UTC-start hourly records** in **2020–2025**. No original BPAT EIA-930 bulk-derived demand entry is missing in these six years. Calculated **unfilled** observed-hour demand sums (MWh under 1 h interval assumption), annual reported demand maxima (MW), peak UTC times and source coverage.

| Year | Valid BPAT UTC hours | Missing original demand | Annual max reported demand MW | Sum of observed-hour demand, MWh |
|---|---:|---:|---:|---:|
| 2020 | 8,784 | 0 | 11,742 | 54,894,812 |
| 2021 | 8,760 | 0 | 10,123 | 55,822,778 |
| 2022 | 8,760 | 0 | 11,068 | 58,346,485 |
| 2023 | 8,760 | 0 | 10,693 | 57,664,188 |
| 2024 | 8,784 | 0 | 11,496 | 59,065,885 |
| 2025 | 8,760 | 0 | 11,537 | 61,103,710 |

This is **EIA-930 demand**, not BPA FERC-714 data. Demand observations are not independently verified billed/retail MWh. Annual source values can be provisional or revised and **must not be interpreted as a climate trend or a validated model target**.

Three independent original EIA API annual ZIP snapshots (BPAT 2021, 2023, 2025) were compared at **the same UTC interval-start hour keys**:

| Year | Paired valid hours | Original old valid→new API blank | Both valid numeric differences | API−old observed common-hour demand sum MWh |
|---|---:|---:|---:|---:|
| 2021 | 8,735 | 25 | 1 | +1,368 |
| 2023 | 8,736 | 24 | 0 | 0 |
| 2025 | 8,760 | 0 | 0 | 0 |

**49 missing/new API source values + 1 changed numeric value = 50 BPAT source-vintage disagreements** over these years. The missing API values are not time keys missing; they are genuine blank demand entries in original later API source records. For 2021/2023 **do not** compare full-year API sum to full-year old sum directly without reporting missing coverage; common-hour pairing was used.

The 2020/2022/2024 BPAT years **were not independently API checked** in this particular analysis. Full-year old-source peak equality with BPA FERC-714 is untested.

## Reproducibility

The user-delivered full source ZIP `C2_BPAT_2020_2025_Real_EIA_Demand_Baseline_Source_Pack_2026_11_25.zip` includes:
- original unmodified 72-month archive and three original BPAT API annual ZIPs;
- actual output: 6-year original annual demand metrics, 3-year later API metrics, strict 3-year paired snapshot comparison, all 50 individual source discrepancies, provenance JSON;
- `reproduce.py`, `test_baseline.py`, README and the original execution JSON.

Verified ZIP CRC; extracted in fresh temporary directory, reran **from packaged original source data**, all four CSV files regenerated **byte-for-byte identical** to bundled results. Five integrity/contract tests passed. Archive SHA256: `4c61e2a2b587c580f50e28483542608a88e8fe3d54ed13141073353ea7eef916` (2,628,018 bytes). No changes were made to frozen originals.

## Operator-source status

The separate `.github/workflows/c2-bpa-ferc714-original-six-year.yml` source downloader has been committed, and [BPA's official FERC-714 report index](https://transmission.bpa.gov/business/operations/ferc714/default.aspx) lists six 2020–25 XLSX originals. However, **this turn did not retrieve or analyze any actual BPA FERC-714 workbook**. The GitHub app connector only exposes workflow data with known run IDs and pull-request filtered commit runs, so the new workflow's **push-run success and source artifacts were not independently verified**. It would be false to claim that annual FERC-714 values were compared. A downloaded operator workbook requires an actual source SHA, workbook schema/measure audit and carefully reconciled definition before any numeric comparison.

**Geographic and scientific gates remain closed:** PUDL service county proxy not an operator-certified annual BA footprint; no observed hourly geolocated demand weights; EIA source vintages conflict in 2021/2023; 2025 is already inspected and not an untouched blind holdout; no model training, climate attribution, SSP/CMIP6 projection or PyPSA system-stress inference. **C-1 frozen.**
