# C-2 E1 — Original SCE and SDG&E 2020 Q1 ZIP privacy/Combined evidence (2026-11-21)

**Original observed public data, NOT imputed county electricity or a fitted weather model.**

Verified real-source [GitHub Actions run 44918996745](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44918996745), **SUCCESS**, published original SHA-pinned source audit artifact **14713061073**. Exact published member `C2_SCE_SDGE_2020Q1_REAL_COMBINED_PRIVACY_QA.json` was downloaded and independently inspected. Inputs are actual publisher SCE XLSX and SDG&E CSV+SHA512 sidecar, pinned in
`scripts/c2_sce_sdge_2020q1_combined_privacy_audit.py`.

## Independently verified original source outcome

| Original source field, January–March 2020 | SCE | SDG&E |
|---|---:|---:|
| Source records | **9,324** | **1,719** |
| Rows per month | **3,108** | **573** |
| `Combined=Y` | **5,055** | **1,421** |
| `Combined=N` | **4,269** | **298** |
| Source positive-kWh cell rows | **3,163** | **543** |
| Original literal zero-kWh cell rows | **0** | **1,176** |
| Blank/missing kWh cells | **6,161** | **0** |
| Extra duplicated `ZIP × month × customer class` rows | **15** | **0** |
| Unique `ZIP × month × class` keys | **9,309** | **1,719** |

Cross-checks from the exact original output:

- **SCE** `Combined=N`: 1,921 positive + 2,348 blank; `Combined=Y`: 1,242 positive + 3,813 blank. SCE has no literal numeric zero kWh cells in the observed real Q1 archive. Missing cells **are not equivalent to observed zero kWh**.
- **SDG&E** `Combined=N`: all 298 positive; `Combined=Y`: 245 positive and 1,176 literal numeric zero. The SDG&E SHA512 publisher sidecar matches original downloaded CSV. A numeric 0 in a source row **does not automatically establish measured zero consumption at that listed ZIP**, especially when `Combined=Y`.
- **SCE duplicate key**: 15 extra `ZIP × month × class` records, confined in the first preview to residential `Combined=Y` and blank kWh/account cells. For example ZIP 93634, 93643, 93664 appear in duplicate key samples for all three months. This is an exploratory diagnostic: the full duplicate reason and any hidden geographic grouping remain **unresolved**. Cannot assume unique `ZIP × month × class` grain or aggregate mechanically.

The original source audit deliberately **does not compute total sales MWh** by summing records across `Combined` categories. Combining donor/recipient ZIPs without the publisher's privacy logic could double count electricity or assign merged consumption to an incorrect ZIP.

## Reproducibility and limits

The actual data were downloaded in the successful CI workflow
`.github/workflows/c2-sce-sdge-2020q1-combined-privacy.yml`,
processed by `scripts/c2_sce_sdge_2020q1_combined_privacy_audit.py`.
Synthetic tests cover blank/zero/non-numeric kWh, duplicate-source accounting
and refusal to approve geography.

The original PG&E public download still returns HTML instead of the
expected ZIP; **not** included in these two-utility empirical counts.
Do not count previous PG&E response HTML as original load data.

## Next data science priorities

1. Find SCE and SDG&E official `Combined=Y` record semantics, including donor ZIP/recipient ZIP, suppression, whether positive kWh are group totals, and why `Combined=N` SCE rows have blanks.
2. Investigate SCE original 15 duplicate ZIP × month × class keys, distinguish true duplicates versus reported structural rows before summing. Keep original source values preserved.
3. For reporting years 2020–2023, expand verified utility ZIP datasets only with source-specific schema/format and version pins.
4. Obtain HUD ZIP–county mapping, classify **unambiguous ZIP support**, **cross-county ZIP**, and **merged/suppressed unknown support** as separate sets. A `Combined=Y` recipient ZIP is not established to be electricity's physical county.
5. Actual EIA861 annual retail sales and CEC annual marginals are different reporting scopes; reconcile only correctly comparable totals. CISO/BA membership remains independently unapproved.

Scientific gate statuses remain
`GEO_LOAD_RELEVANCE=BLOCKED`,
`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`,
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`,
`model_training_permitted=false`.
No C-1 materials changed.
