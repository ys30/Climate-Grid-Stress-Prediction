# C-2 E1 — SCE / SDG&E 2020 Q1 observed non-combined positive source screening (2026-11-21)

**Recalculated from independently successful actual source-audit CI [44918996745](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44918996745)**, artifact **14713061073**, downloaded exact JSON member `C2_SCE_SDGE_2020Q1_REAL_COMBINED_PRIVACY_QA.json` SHA256
`cd58f2e39b96e2064ad58367fe7eb26e9d6796a6cda464cd1a0cf09675f7d74e`.

This is **source-observation screening, not published actual ZIP-by-county load allocation**.

| Original Q1 row category | SCE | SDG&E |
|---|---:|---:|
| All original source rows | 9,324 | 1,719 |
| `Combined=N` and positive source `TotalkWh` | **1,921** | **298** |
| `Combined=Y` and positive source `TotalkWh` | 1,242 | 245 |
| `Combined=N` but source kWh blank | **2,348** | 0 |
| `Combined=Y` and source kWh blank | 3,813 | 0 |
| `Combined=Y` and literal source kWh zero | 0 | 1,176 |
| Percent original rows both non-combined and positive kWh | 20.6027% | 17.3357% |

The **2,219 rows** with positive `TotalkWh` and `Combined=N`
across both utilities are **candidates for a conservative future ZIP
support/territory cross-check**, not independently identified metered
electricity at that ZIP or known county allocation.

There may be source reporting overlap across SCE and SDG&E service
territories; source rows are not unique ZIP IDs or customers and must not
be summed as individuals. The SCE source also has 15 excess
`ZIP × month × customer class` repeated keys; their original Excel
rows must be inspected before any deduplication. ZIPs may cross county
boundaries; source electricity may be net of behind-the-meter generation;
the historical utility-to-CISO membership crosswalk is not certified.

## Live 2020–23 acquisition tasks

- The authentic SDG&E [2020–2023 16-quarter publisher SHA512 workflow](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44920136951) was **queued** at last verification. The earlier run 44920034129 **failed** at a synthetic test fixture; corrected in `57ff43b8952e58ddd47bb38354c9d88fa38b5c31`. Do not claim all 16 original quarterly sources verified until current run succeeds and its artifact is audited.
- The original SCE [2020 Q1 exact duplicate raw-row audit](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44919918078) was **queued**, so the 15 same-key rows are empirically observed but precise cause/unicity is still unverified.
- New original official-index [SCE 2020–2023 16-quarter source collector](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/workflows/c2-sce-16-quarter-official-index.yml) discovers the actual XLSX historical hrefs from SCE's quarterly reports page, instead of assuming stable paths; original source verification result is **not yet confirmed**.

Official website confirms historical publicly listed XLSX quarterly reports 2020–23:
https://www.sce.com/regulatory/regulatory-information/energy-data-reports-compliances
and SDG&E original CSV & publisher HASH sidecars:
https://energydata.sdge.com/homePage

**No source geometry approved, no joined county MWh, no E2 fit, no SSP forecast or other modeling.**
`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`,
`GEO_LOAD_RELEVANCE=BLOCKED`,
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`,
`model_training_permitted=false`.
2024–25 EIA-930 demand holdout remains unused for model tuning; C-1 untouched.
