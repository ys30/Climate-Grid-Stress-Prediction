# C2 E1 — State-specific historic utility–BA county-source gaps (2026-11-17)

**Real source association data, independently re-read from frozen PUDL v2026.10.0 GitHub Actions artifact 14144934238; not sales-MWh or electric demand geographic coverage. C-1 frozen, E2 training blocked.**

## Source evidence
Outer archived source `github-actions-artifact-14144934238.zip`; immutable inner `EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv` SHA256 `957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`. Independent Python re-read validates **1418** unique year–BA–utility–state entries and **1382** unique year–utility–state source keys, 28 of which reference multiple target BAs. Data were grouped by BA, utility state and pre-held-out vs source-only period: 2020–2023 and 2024–2025, producing 24 BA–state–period rows.

## Actual original-data geographic-source coverage, 2020–2023

| BA | State | Association rows | County-source matched | Unmatched | Excluded other-state county-association slots |
|---|---|---:|---:|---:|---:|
| AZPS | AZ | 96 | 48 | **48** | 0 |
| SRP | AZ | 33 | 8 | **25** | 0 |
| CISO | CA | 351 | 150 | **201** | 7 |
| CISO | AZ | 6 | 0 | **6** | 0 |
| CISO | NV | 4 | 4 | 0 | 12 |
| BPAT | OR | 146 | 142 | 4 | **250** |
| BPAT | UT | 6 | 4 | 2 | 20 |
| BPAT | WA | 179 | 178 | 1 | **226** |
| BPAT | ID | 72 | 72 | 0 | **104** |
| BPAT | MT | 24 | 24 | 0 | 44 |
| BPAT | NV | 8 | 8 | 0 | 40 |
| BPAT | WY | 8 | 8 | 0 | 32 |

Unmatched source association rows, excluded cross-state county-association slots and customer/retail MWh are *three distinct units* and must never be summed or equated. The original **64 multi-BA association records** remain a subset of the matched/unmatched association universe; they are not new source rows.

## Operational priorities from the evidence
1. **CISO California:** 201/351 county-unmatched source associations: audit EIA861 utility reporting / county source linkage and real sales contribution first.
2. **AZPS and SRP Arizona:** 48/96 and 25/33 county-unmatched respectively, including multi-BA utility source associations; do not attribute one utility's entire sales to an exclusive BA polygon.
3. **BPAT OR/WA/ID:** nominally high matched association counts coexist with very large excluded cross-state county slots (250 OR, 226 WA, 104 ID during 2020–2023); track state-boundary service territory loss independently from matched-association share.

## Restrictions and next empirically decisive evidence
An official PUDL v2026.10.0 `core_eia861__yearly_sales.parquet` source is not yet verified downloaded or decoded. The existing Actions workflow is configured to obtain it from versioned public S3, but no independently verified successful workflow run and **no empirical sales_mwh or customer coverage result** is available. Consequently this state-level audit can prioritize source repair, but **cannot validate historical BA load geography or approve E2 model training**.

No 2024–2025 demand test observations were accessed in this grouping; only previously published original PUDL source association metadata from those years was included to check long-term source completeness. All C2 science gates remain blocked, `model_training_permitted=false`. C-1 remains frozen.
