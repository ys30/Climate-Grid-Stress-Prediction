# C2 E2 — Source-verified event registry, training and validation only (2020–2023)

Date: November 15, 2026. **Independent source QA completed; original values unchanged; C-1 frozen.**

## Primary source and computation
Downloaded successful original full source GitHub Actions artifact 14127710411 (run 43629200989): ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`, inner 210,432-BA-hour CSV.gz SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. A fresh independent local Python run read the actual source and **excluded all 70,176 source BA-hours of 2024–2025** before candidate-event construction.

The 2020–2023 source has 68 original flagged BA-hours and two separately identified, originally unflagged extreme SRP hours at 2023-02-27 00:00Z and 01:00Z. Group consecutive flagged hours within the *same BA* (including these two secondary candidates), with no hour imputation, yields **27 contiguous candidate episodes totaling 70 flagged/source-diagnostic hours**.

| BA | Contiguous candidate episodes | Candidate hours |
|---|---:|---:|
| AZPS | 7 | 12 |
| BPAT | 0 | 0 |
| CISO | 0 | 0 |
| SRP | 20 | 58 |
| **Total** | **27** | **70** |

There are **21 events** whose reported peak exceeds 3× the observed unflagged reference median at the same UTC hour from up to seven days before/after (excluding the center date), and **eight events** exceeding 10× that descriptive reference. This is not a validated weather-adjusted demand baseline and does not prove an EIA source error.

## Three priority observed event peaks

| BA | Peak hour start UTC | Reported demand MW | Peak / same-UTC-hour reference median |
|---|---|---:|---:|
| AZPS | 2020-01-22 15:00Z | 101,412 | 30.923 |
| SRP | 2023-02-26 23:00Z | 68,520 | 23.326 |
| SRP | 2023-06-03 20:00Z | 70,313 | 15.131 |

The February 2023 SRP anomaly now forms **one contiguous five-hour candidate episode** (original flagged neighboring hours plus two independently detected missed hours). This prevents mistaking hourly screening labels for independent energy-system events.

## Research decision and publication restrictions
- These are *candidate source anomaly episodes*, not 27 verified errors or actual grid-stress events. Neither EIA's historical reporting revisions nor the source BA operator has confirmed these peaks are wrong.
- Annual peak and P99.9 robustness must be reported with preserved original statistics, plus *explicitly diagnostic* candidate-hour omission scenarios, never silently modified data.
- No inference is allowed from a BA mask or Census population estimate to electric meter/customer-load exposure. The original 2018 HIFLD, TIGER county and population proxy masks remain geographically unapproved.
- Sealed 2024–2025 test has not been inspected for this screen. `model_training_permitted=false`; no GAM/XGBoost, historical ALL/NAT, or future SSP/PyPSA claims are made.
- Full 27-event row-level CSV, SHA256 audit JSON, human-readable research report, and independent Python script are packaged in the project conversation as `C2_E2_2020_2023_VERIFIED_EVENT_REGISTRY_20261115.zip` (ZIP SHA256 `1b352918b0e94ecca7457f8f626520ef21d1de5076db57403abf19baebed2500`).
