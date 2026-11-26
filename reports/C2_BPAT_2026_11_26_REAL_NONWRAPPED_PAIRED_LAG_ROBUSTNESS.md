# C-2 BPAT — authentic-source nonwrapped weather-load lag sensitivity (2026-11-26)

## Independent correction to earlier temporal-shift placebo

The preceding 2,000-draw test circularly shifted the monthly candidate ERA5 cold indicator and **wrapped last-day conditions to the first days of the same month**. This is a deliberately artificial negative control, not a physical-weather time series. To test whether that artifact dominates findings, the current analysis uses **nonwrapped ±3, ±5, ±7, ±10 and ±14 calendar-day shifts** within every year-month, discarding hours without valid within-month exposure on each shift.

**Critical paired comparison:** for each offset, the contemporaneous zero-lag odds ratio is recomputed on **exactly the same response-hour subset** as the shifted-exposure odds ratio. Comparing the full-sample OR directly to the lagged OR would confuse timing with changing sample composition.

## Actual original-source checks

Re-read original archived source ZIP `C2_2020_2025_72_Month_Original_Source_Archive.zip` (SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`); exact gzip SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. BPAT has **52,608** unique hourly UTC EIA930 loads and candidate-area ERA5 temperatures. Same six-year original exposure/outcome as earlier: cold = ERA5 candidate-area 2m temperature ≤ -5°C deviation from its year×month×UTC-hour mean; high demand = load above year×month 95th percentile. Strata: 72 year×month cohorts. Both outcomes and exposures are **original observed source data under an unapproved geographic proxy**.

| Offset | Matched load hours | Same-hour OR on paired support | Nonwrapped shifted OR |
|---|---:|---:|---:|
| -3 d | 47,424 | 5.927 | 1.402 |
| +3 d | 47,424 | 6.088 | 1.855 |
| -5 d | 43,968 | 5.571 | 1.109 |
| +5 d | 43,968 | 6.047 | 0.904 |
| -7 d | 40,512 | 4.628 | 1.178 |
| +7 d | 40,512 | 6.500 | 1.067 |
| -10 d | 35,328 | 4.437 | 1.040 |
| +10 d | 35,328 | 7.423 | 1.296 |
| -14 d | 28,416 | 5.006 | 1.494 |
| +14 d | 28,416 | 7.018 | 1.178 |

Every nonwrapped delayed/advanced exposure OR is smaller than its **paired, same-response-hour** reference OR. The test is deterministic, not a null-randomized distribution and cannot supply a new significance level.

## Delivered reproducibility

- **Actually executed** locally on the locked original six-year source; script rerun, JSON log, derived CSV, full SHA256 manifest, README.
- Download ZIP `C2_BPAT_2026_11_26_Nonwrapped_Weather_Load_Lag_Audit.zip`, CRC passed, SHA-256 `1e31a5b45dfbc3368016a25f971611927385c96e0bc533e2695e59808107da2a`.
- GitHub source `scripts/c2_bpat_era5_nonwrapped_paired_lag_audit.py` and results `results/source_only/BPAT_2020_2025_ERA5_NONWRAPPED_LAG_3_5_7_10_14DAY_PAIRS.csv` were independently authored to implement this design. The **download ZIP contains the exact locally executed script**; the GitHub source should be run under its own CI before claiming exact-code execution.

## Limitations and next research actions

- Weather temperature comes from a candidate BA geographic area, **not yet approved historical BPAT footprint**. This remains a strong barrier to causal or official weather attribution.
- Related high-demand hours inside the same storm are highly dependent; even nonwrapped lag sensitivity does not identify a climate-change trend or policy intervention effect.
- Month-specific outcome thresholds are exploratory, selected with full-period observations, and 2025 is **not** a blind holdout.
- Historic FERC714 BPA respondent identity 122 → PUDL 21 → XBRL C002357 is source-supported, but actual fixed-version v2026.10.0 respondent-21 hourly rows remain unverified, preventing FERC/EIA measurement comparison.
- Next scientific step should validate alternative weather-geographic masks and EIA demand source-vintage anomalies before a preregistered event-level or conditional model. CMIP6/SSP/PyPSA future scenario runs are **not** complete.

**C-1 remains frozen, C-2 inference gates remain closed.**
