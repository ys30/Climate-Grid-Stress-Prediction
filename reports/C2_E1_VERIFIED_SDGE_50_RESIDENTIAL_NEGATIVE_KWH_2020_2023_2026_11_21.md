# C-2 E1 — independently verified 50 SDG&E residential negative kWh cells (2026-11-21)

**Original evidence, not a causal explanation or county MWh allocation.**
Verified source [GitHub Actions run 44922065108](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44922065108) **SUCCESS**,
artifact **14713863065**, downloaded and independently parsed. Each of the
16 original SDG&E CSVs for 2020–2023 matched the same publisher's
corresponding original SHA-512 sidecar. Original ZIP source manifest
member: `C2_SDGE_REAL_2020_2023_16_QUARTER_PROVENANCE.json`.

## Source observations

27,504 original ZIP × month × customer-category report records across
2020–2023, no duplicate ZIP/month/class source keys, and exactly
**20,394 literal zero `TotalkWh`**, **7,060 strictly positive**
and **50 strictly negative** rows. These cell counts sum to 27,504.
Source privacy flag `Combined=Y` occurs in 23,506 source rows.
The 50 negative records are all source `CustomerClass=R`
(residential), and none occur in 2020–2021.

| Source quarter | Negative kWh rows |
|---|---:|
| 2022 Q2 | 18 |
| 2022 Q3 | 4 |
| 2023 Q1 | 1 |
| 2023 Q2 | 27 |
| **Total** | **50** |

Independent original combined-flag split:
`Residential, Combined=N` **28 rows**;
`Residential, Combined=Y` **22 rows**.
Thus the negative rows are **not confined** to privacy-combined reported ZIPs.

Month/class/Combined counts are preserved within each original quarterly
manifest record at `negative_kwh_original_class_combined_month`.

## Scientific interpretation

Negative reported net electricity use may reflect customer-side
generation, net metering or reconciliation accounting, but this audit
does **not** establish any of these causes. Do not convert negative
kWh cells to zero, discard them as bad data, or treat the
`Combined=Y` zero values as physically zero use. Need utility
codebook/accounting scope and net-metering disclosure documentation
before interpreting the measured quantity. The 50 rows also do NOT
represent 50 negative BA hourly EIA-930 demands.

Original publisher download URLs and source SHA512 integrity are
handled in `scripts/c2_sdge_real_2020_2023_sixteen_quarter_source_audit.py`;
new original negative disaggregation was repaired from a malformed
newline injection without weakening the source SHA checks.

C-2 existing scientific gates remain:
`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`,
`GEO_LOAD_RELEVANCE=BLOCKED`,
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`,
`model_training_permitted=false`.
No 2024–25 hourly demand test set used; no C-1 modifications.
