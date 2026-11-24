# C-2 BA-0 — independent 2025 bulk SHA corroboration and tested raw-byte comparator (2026-11-23)

## Verified new external evidence

An independent public third-party [Gridprims 2025 EIA-930 consistency ledger](https://gridprims.com/ledger/checks/) explicitly records the following SHA-256 values for EIA official bulk BALANCE datasets:

| File | Independently published SHA-256 | Archived old source SHA | Exact hash agreement |
|---|---|---|---|
| EIA930_BALANCE_2025_Jan_Jun.csv | `fac4bb991dfa1dab3b4b35300ccab54ac99be13a40ce91954db8ddafb2816242` | same | yes |
| EIA930_BALANCE_2025_Jul_Dec.csv | `1146158b972439db7c7f4cc7d0491e07644ddbf244d03b8ecb44cb2c833d10f1` | same | yes |

The ledger labels its sources as an October 2026 EIA six-month snapshot. These independently corroborated hash **strings** cover **223/325 previously known conflicts** (2025 Jan–Jun 48, Jul–Dec 175). **Important**: the source file **bytes were not downloaded here**, and independent publication of SHA values does not itself prove which source values EIA revised or why API differs from the bulk snapshot. Two retrieval methods failed in this session; EIA current download remains unavailable for direct byte inspection.

## Executed additional diagnostics

Read actual archive-based `CONFLICT_325_HE_BYTE_ACQUISITION_QUEUE.csv`. The **169 AZPS 2025 old-vs-API numeric conflicts occur on only 16 UTC dates**, rather than uniformly across the year. **36 of 169 changed hours exceed 1,000 MW in absolute demand difference**; a large magnitude discrepancy alone does not prove a source error. Produced a reproducible 16-date grouping CSV.

Authored and locally executed a fail-closed `check_current_bulk_bytes.py` utility:

- Requires exactly 325 unique BA×UTC conflict keys and correct UTC hour-ending = UTC start + 1 hour.
- Accepts five authentically obtained `EIA930_BALANCE_YYYY_Half.csv` files in an explicit local folder; checks each **entire** source file SHA against frozen original; detects repeated raw HE keys; compares each actual raw BA/HE demand with both archived vintage values.
- Correctly reports `not_obtained` when a file is not present; no fabricated CSV, no silent imputation or training-data approval.
- **3 local tests passed** for raw EIA HE parsing, duplicate rejection and missing/invalid numeric preservation. With no new bulk files present, real 325-conflict queue execution returned `bulk_files_obtained=0`, `origin_revision_cause_established=false`, `model_training_permitted=false`.

The user-delivered, SHA-verified ZIP `C2_EIA_2025_Independent_SHA_CrossCheck_And_ByteGate_2026_11_23.zip` contains the full Python program, tests, 325-row original queue, AZPS 16-date results, actual fail-closed output JSON, reproducibility README and manifest. ZIP SHA256 `497fdf57c20beac1c377eefa3d35e48eff1b3c5c1aa82b5454b94e04df5eda7a`. The source-archive ZIPs remain separately available in the previous delivered packages, not published here.

## Interpretation

The outside ledger substantially strengthens independent provenance of the **two original 2025 bulk-file identities** but **does not resolve** the 325 source-vintage disagreements. No raw official bytes were acquired; no canonical selection of old vs API values. All BA historical operating geography is still unapproved for demand-weighted weather exposure; 2025 already explored descriptively; no model fitting, causal climate attribution, CMIP6 prediction, or PyPSA grid stress inference is authorized. C-1 frozen.

Next: obtain the two authentic 2025 official bulk source files from EIA or a trustworthy archival source and run the byte comparator. When original file SHA matches, compare raw HE values to archived old-vs-API values; then use release metadata to investigate whether API changed at a different snapshot time.
