# C-2 EIA-930 extreme spike audit: immutable dual-vintage evidence, 26 November 2026

## Actually rerun against the original 210,432-row archived dual-vintage panel

Source: `C2_C2_EIA930_Dual_Vintage_210432h_Quarantine_2026_11_23.zip` and its true archived `results/C2_2020_2025_DUAL_VINTAGE_QUARANTINE_NOT_MODEL.csv.gz` (210,432 BA×UTC-hour rows). No remote API values were invented; archive rows explicitly distinguish **API_YEAR_NOT_FETCHED_FOR_COMPARISON** from **IDENTICAL_NUMERIC**.

The executed local script `c2_eia_source_spike_window_audit.py` recomputed **five 9-hour event windows (45 source-hour records)** around the known AZPS, SRP and BPAT spike anchors, using the median of six outside-reference hours in each window (relative offsets −4,−3,−2,+2,+3,+4 hours). Four actual-source Python tests passed (4/4); the source flags were preserved exactly, and no missing API numbers were filled. CSV summary committed as `results/source_only/C2_EIA930_FIVE_SPIKE_DUAL_VINTAGE_NINE_HOUR_QA.csv`.

| Spike BA & anchor UTC | Bulk MW | Anchor / six nearby reference-hour median | API 9-hour coverage | Matching values / covered | Source anomaly flags in window |
|---|---:|---:|---:|---:|---:|
| AZPS 2020-01-22 15:00 | 101,412 | **37.11** | 0 | N/A | 3 |
| AZPS 2020-09-03 16:00 | 21,020 | **4.75** | 0 | N/A | 3 |
| SRP 2023-02-26 23:00 | 68,520 | **20.43** | 9 | **9 / 9** | 3 |
| SRP 2023-06-03 20:00 | 70,313 | **14.90** | 9 | **9 / 9** | 3 |
| BPAT 2020-11-25 23:00 | 11,742 | **1.59** | 0 | N/A | 0 |

**Novel source-QA finding:** In the 9-hour SRP February 2023 window, the post-anchor 2023-02-27 00:00 UTC **45,097 MW** and 01:00 UTC **27,030 MW** records are **unflagged** despite being more than threefold the six-hour outer-reference median. Both API and bulk values match at all nine hours. This means relying exclusively on original anomaly flags will miss suspicious neighboring hours in the same event. Two matching vintages only establish persistence of the recorded value, **not** physical plausibility or an operator-certified measurement.

For AZPS and BPAT 2020, later API source years have **not been obtained** in this archive, so no cross-vintage conclusion is possible. BPAT November 2020 may represent a multi-hour physical event or a reporting anomaly; its lower local amplitude ratio is not evidence of authenticity. Do not automatically remove spikes based on this exploratory ratio.

## Scientific implications

1. Keep immutable original-bulk figures; distinguish `source_flagged`, `unflagged_event_neighbor_review`, and `missing_API_year` fields.
2. Establish a **date/hour-wide review envelope**, not solely drop flagged hours, for future **sensitivity-only** modelling. Before any final deletion, check operator/BPA/SRP/APS source records, time conventions, outages, system load vs interchange and genuine API source bytes; a newer API serving the same value does not certify it.
3. Formal daily peak weather model stays BLOCKED. Original daily model sensitivities (AZPS and SRP large slope/RMSE changes on flagged-day exclusion) remain warning flags, not approved coefficients.
4. The 2020–2025 ERA5 geographical BA proxies and PUDL FERC714 respondent 21 core-hourly verification remain unapproved/pending; no attribution or SSP prediction claims arise from this QA.
5. **C-1 remains frozen.**

## Reproducibility

The actual executed script, four actual-source tests, logs, 45-hour context CSV, five-spike source-vintage gate CSV and source SHA-256 manifest are in the verified local bundle `C2_EIA930_2026_11_26_FiveSpike_Window_Vintage_Repro.zip`, SHA-256 `3558b6a31907e7298ee5c353a68e0a06dc6c5846f31bdc621a1fcb0da42577b3`, ZIP CRC confirmed. This bundle references, rather than duplicates, the separately archived 210,432-row original dual-vintage ZIP. The exact GitHub summary CSV is an authored result representation; compare to downloaded CSV to confirm byte-exact identity. The local script is provided in the reproducibility bundle, not claimed CI-passed on GitHub.
