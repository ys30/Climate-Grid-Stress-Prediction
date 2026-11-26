# C-2 BPAT — day-block bootstrap and seasonal cold-load tail robustness (2026-11-26)

## Actually executed on archived original EIA930 × candidate ERA5 observations

The real 72-month archived source ZIP `C2_2020_2025_72_Month_Original_Source_Archive.zip` was re-opened in the local scientific runtime and **verified SHA-256** `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`. Input is a 52,608-hour 2020–25 BPAT UTC source cohort with recorded EIA930 MW demand and candidate ERA5 2m temperature. The ERA5 historical BA spatial proxy is **not operator-approved**.

### Revised design reduces obvious time confounding

1. High-load target is now **top 5% within each calendar year × month**, not a single pooled six-year cutoff that would inherently favor recent higher-load years and winter.
2. Cold exposure is **≤ −5°C from the same year × month × UTC-hour mean candidate ERA5 temperature**, not a pooled six-year month-hour temperature baseline.
3. Mantel–Haenszel (MH) pooled odds ratio is calculated across **72 year-month groups**, **67 of which have an informative cold/warm contrast**. This is an observational within-year-and-month comparison, **not causal attribution**.
4. To avoid using independence of adjacent hourly observations for the reported uncertainty, re-sample complete **UTC days** within each year-month with replacement; run **500 seeded iterations**, using seed 20261126. Output the percentile interval and all bootstrap draws. This retains within-day clustering but does not fully account for multi-day weather event persistence. Full independent-hour confidence intervals are intentionally **not** used as the primary uncertainty estimate.
5. Leave one complete year out and change the exposure thresholds −3/−5/−7°C. Preserve the full original source for primary analysis. Temporarily omit four candidate source-anomalous 2020 hours as a clearly labeled, nonapproved sensitivity only.

### Actual observed results

| Metric | Result |
|---|---:|
| Source BPAT hours 2020–25 | **52,608** |
| Within-year-month top-5% demand hours | **2,664** |
| Cold-anomaly hours (≤−5°C, adjusted by year-month-UTC-hour) | **3,946** |
| Cold hours with top-5% demand | **706 / 3,946 = 17.89%** |
| Other hours with top-5% demand | **1,958 / 48,662 = 4.02%** |
| Year-month stratified MH odds ratio | **6.05** |
| Daily-block bootstrap 95% percentile interval, 500 draws | **[4.90, 7.47]** |
| Sensitivity excluding four unreviewed 2020 hours, original definitions fixed | **6.06** |

**Threshold sensitivity** for the within-month-year 5% high-load definition:

| Cold threshold | MH odds ratio |
|---|---:|
| ≤−3°C | **3.89** |
| ≤−5°C | **6.05** |
| ≤−7°C | **9.24** |

**Leave-one-year-out** odds ratios: omit 2020: 5.93; omit 2021: 6.48; omit 2022: 5.49; omit 2023: 5.75; omit 2024: 6.57; omit 2025: 6.11. There is no single omitted year that eliminates the descriptive association.

## What the evidence does and does not establish

- **Supported:** strong descriptive association between cold deviation and high BPAT original EIA930 hourly demand under multiple season- and time-stratified exploratory definitions, on a **candidate** ERA5 weather proxy, not only a pooled-year winter artifact.
- **Not supported yet:** independent BA geospatial exposure validation, a weather-induced causal demand increment, non-autocorrelated event-independent uncertainty, any untreated held-out prediction, 2020 source spike approval, true FERC714 cross-source comparison or future CMIP6/SSP/PyPSA grid stress predictions.
- The 500 daily-block resamples are conditional on data-defined thresholds/anomalies. Daily blocks still split multi-day cold spells and are **descriptive robustness intervals, not publishable causal confidence intervals**.
- The cold thresholds and 5% load target are exploratory choices; no multiple-comparison-adjusted confirmatory hypothesis test is claimed.
- Cross-vintage EIA930 conflicts persist, and the historical BPAT BA geography is explicitly not approved.

## Reproducibility

A real executed self-contained analysis script, input checks, JSON manifest, all **500 individual bootstrap OR draws**, year-omission table, threshold table, README and execution log have been ZIP-archived. File: `C2_BPAT_2026_11_26_ERA5_Cold_Load_DayBlock_Robustness.zip`, SHA-256 `f7b5e20beb79e9d02ab952c5cd973a1f3ba82dbea00506b772d5417f83676ae5`. ZIP CRC check passed; eight files archived.

Repository result table: `results/source_only/BPAT_2020_2025_ERA5_COLD_THRESHOLD_STRATIFIED_MH_ROBUSTNESS.csv`.

## Scientific next step

Use a **weather-event block** robustness scheme (e.g., 5–7 day blocks) and, if feasible, a conditional logistic / hierarchical model accounting for year-month-hour, long-term load changes and alternative BA weather masks, with the 2020 demand spike source audit. Complete actual PUDL FERC714 respondent 21 hourly source retrieval and verify reporting scope separately. Only then consider formal historical climate attribution or future stress forecasts. **C-1 frozen, C-2 operational and attribution gates remain closed.**
