# C2 E2 — Full 2020–2023 training/validation EIA-930 anomaly screen

Date: 2026-11-14 Mountain. **Independent archived source-data diagnostic; original demand unchanged, no model admitted.**

## Source verified
- GitHub Actions run 43629200989, artifact 14127710411, original full panel ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`.
- Inner 210,432-BA-hour .csv.gz SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.
- Reviewed only **2020–2023**: 140,256 archived BA-hour rows (AZPS, BPAT, CISO, SRP). The 2024–2025 test set was removed before computing rolling medians.

## Second independent retrospective sensitivity rule
For each BA separately, use the original valid demand values from the prior 24 and following 24 UTC hours (excluding center) to form a local median. Require at least 12 valid values on both sides. Flag >=3× or <=1/3× local source median. Original flagged hours remain in the reference data and values are never altered. The new rule is **exploratory diagnostic**, not a prespecified model exclusion policy.

| BA | Existing 2020–2023 source flags | Independent candidates | Previously unflagged new candidates |
|---|---:|---:|---:|
| AZPS | 12 | 3 | 0 |
| BPAT | 0 | 0 | 0 |
| CISO | 0 | 0 | 0 |
| SRP | 56 | 20 | 2 |
| **All** | **68** | **23** | **2** |

The original source's full six-year 70 flags contain two more events in the sealed 2024–2025 test period; they were not part of this reanalysis.

Newly detected source-screen candidates:
- **SRP 2023-02-27 00:00 UTC:** 45,097 MW vs 3,099 MW local median, 14.552×.
- **SRP 2023-02-27 01:00 UTC:** 27,030 MW vs 3,107 MW local median, 8.700×.

This whole-training/validation-window check finds exactly the same two previously unflagged SRP hours as the earlier restricted near-event scan, but is **not proof of absence of other data problems or of EIA reporting error**. The differing screen totals (68 source flags versus 23 local-median candidates) reflect different detection definitions and related-neighbor marking.

## Decision and next falsifiable check
Obtain a second independently archived EIA-930 source/vintage or the per-BA Excel reference (with original reported extreme notes) and compare original values and hour-ending timestamp labels. The available source contains genuine, unusual reported values but no verified revision/correction information yet. Keep all source values unchanged and distinguish source flags from confirmed exclusions.

Historical BA electricity-load geography and weather exposures remain unapproved; E2 model fitting, ALL-vs-NAT attribution and SSP/PyPSA stress projection claims remain blocked. `model_training_permitted=false`; C-1 frozen.

A complete reproducible local report, per-BA summary CSV, row-level candidate CSV, audit JSON and source-Python script are attached as `C2_E2_FULL_TRAIN_VALIDATION_ANOMALY_SENSITIVITY_2026-11-14.zip` in the conversation.
