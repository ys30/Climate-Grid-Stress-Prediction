# C-2 milestone — four-BA original-source cold-load heterogeneity (2026-11-26)

## Scope and actual execution

This turn **actually re-ran exploratory analysis** on the original SHA-pinned archive `C2_2020_2025_72_Month_Original_Source_Archive.zip` (SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`), containing member `C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz` (SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`). **210,432** real source BA×UTC-hour records across BPAT/AZPS/CISO/SRP, 2020–25. Of these **260 demand values are absent**; all candidate ERA5 temperatures present. Every row's geography and model-training admission flags are FALSE.

Definitions are *identical by BA*: (i) high load strictly exceeds the BA×year×month observed nonmissing EIA930 demand P95; (ii) cold anomaly ≤−5°C relative to that BA×year×month×UTC-hour candidate ERA5 mean; (iii) year-month-stratified Mantel–Haenszel pooled odds ratio on nonmissing original-demand hours. These are **descriptive in-sample associations, NOT weather causal effects**. The BA ERA5 geographic proxy (HIFLD-era candidate) is NOT operator-certified, and EIA demand is original bulk vintage (cross-API-vintage disagreements unresolved).

## Main observed differences

| BA | Valid observed demand hours | Missing | Cold + high-load hours | Within-month-year MH OR |
|---|---:|---:|---:|---:|
| AZPS | 52,582 | 26 | 221 | 1.372 |
| BPAT | 52,608 | 0 | 706 | **6.048** |
| CISO | 52,499 | 109 | 79 | **0.639** |
| SRP | 52,483 | 125 | 198 | 1.225 |

BPAT **6.047548** reproduces the previous single-BA source-based analysis. In the source-announced anomaly-flagged-hour omission sensitivity, full-year MH OR remains BPAT 6.048, AZPS 1.376, CISO 0.639 and SRP 1.225. **This does not remove the unflagged 2020 BPAT spike**, which needs separate independent vetting.

### Important season effect modification — avoid a unified cold coefficient

On the November–March subset, the descriptive MH odds ratios are: **BPAT 19.90, AZPS 4.26, SRP 4.16 and CISO 3.13**. On April–October, BPAT is **2.52**, CISO **0.148**; AZPS and SRP show **zero cold×high-load co-occurrence hours** under the selected tail/exposure definitions (an ordinary finite positive MH estimate is unavailable). No confirmatory tests of BA×season interaction have yet been conducted. These exploratory season splits are sensitive to source threshold definitions, geographic masks and small cold×tail cells. A −5°C *anomaly* is not always physically cold.

This distinction is substantively important: **CISO full-year MH OR <1 but winter-only >1**, and BPAT winter-only strongly exceeds its full-year value. C-2 should pre-specify BA×season terms and avoid generalizing the BPAT winter relationship to the entire West.

## Sensitivity to removing one year

| BA | Range of six leave-one-year-out full-year MH OR |
|---|---:|
| BPAT | **5.49–6.57** |
| AZPS | **1.25–1.56** |
| CISO | **0.55–0.73** |
| SRP | **1.10–1.44** |

These ranges summarize observed deletion sensitivity and are **not 95% confidence intervals**.

## Source QA / data scope

| BA | Missing EIA load | Source-flagged anomaly candidates | Candidate ERA5 temp missing |
|---|---:|---:|---:|
| AZPS | 26 | 12 | 0 |
| BPAT | 0 | 0 | 0 |
| CISO | 109 | 1 | 0 |
| SRP | 125 | 57 | 0 |

The original archive does not flag the known unusual BPAT November 2020 hourly spike; a zero flagged count is NOT an assertion of error-free records.

## Deliverables and reproducibility

Actual local executed script: `c2_four_ba_cold_load_source_audit.py`, full original 72-month input archive, source-reported annual/hourly tables, QA CSV, winter/nonwinter comparison, leave-year-out CSV, README and SHA manifest were packaged into `C2_2020_2025_Four_BA_Cold_Load_Comparison_RealSource_2026_11_26.zip`, **SHA-256 `63a5cde3788f72b59ba5a97919019110b39aa8f80b8a320c2cff94e9ec092cff`**, ZIP CRC verified.

Github:
- `results/source_only/C2_FOUR_BA_2020_2025_COLD_LOAD_MH_OBSERVED_UNAPPROVED.csv`
- `results/source_only/C2_FOUR_BA_2020_2025_WINTER_NONWINTER_ASSOCIATION.csv`
- `scripts/c2_four_ba_original_eia_era5_cold_load_exploratory.py` (separately authored portable implementation of same methodology, **not yet independently executed in CI**).

## Research-stage evidence and next decisive step

This is the first direct multi-BA *actual observed source* contrast of candidate cold-load associations. It establishes **heterogeneous exploratory associations** under one analysis design, not officially approved BA climate exposure or estimated causal differences. Practical research upgrades:

1. For **all four BAs**, replicate winter and nonwinter contrasts using a genuinely distinct, documented BA geographic weather mask (the 2023/2025 selected-month TIGER vs HIFLD QA already demonstrates mask differences; cannot declare six-year mask robustness from four months).
2. Independently audit anomalous source-vintage load spikes and EIA API disagreements; use original bulk vintage as immutable baseline and disclose other vintages.
3. Acquire *actual* PUDL v2026.10.0 FERC-714 respondent 21 original core hourly source rows for BPAT. Historical respondent identity is supported (legacy 122 → PUDL 21 → XBRL C002357), but **genuine 2020–25 FERC hourly values/coverage remain unverified**.
4. Develop pre-specified multi-BA interaction/event-block model after reliable exposure geography and statistical dependence plan. No valid historical weather attribution coefficient or 2030/40/50 CMIP6-SSP/PyPSA model outcome can be claimed yet.

**C-1 frozen and untouched.**
