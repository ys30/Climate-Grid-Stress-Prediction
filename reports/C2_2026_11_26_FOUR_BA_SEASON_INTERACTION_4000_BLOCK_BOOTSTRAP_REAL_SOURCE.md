# C-2 four-BA season heterogeneity — actual original-source 4,000 clustered resamples (2026-11-26)

## Direct original-data reanalysis

The SHA-locked `C2_2020_2025_72_Month_Original_Source_Archive.zip` (SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`) and real original member `C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz` (SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`) were re-read in the executing environment. Exactly **210,432** four BA-hour source records (AZPS/BPAT/CISO/SRP), **210,172** original nonmissing demand values, and candidate-area ERA5 temperature were read. No geospatial/weather proxy is operator-certified.

Using uniform, exploratory in-sample definitions: weather exposure ≤−5°C relative to BA×year×month×UTC-hour candidate temperature mean; high load > BA×year×month P95 of nonmissing original EIA930. Mantel–Haenszel (MH) within each year×month stratum, split winter Nov–Mar (30 monthly strata) vs nonwinter Apr–Oct (42 strata). Computed all four 2×2 counts from the **real hourly rows**, not prefilled tables.

### Observed winter and nonwinter counts

| BA | Winter cold+high | Winter MH OR | Nonwinter cold+high | Nonwinter MH OR |
|---|---:|---:|---:|---:|
| AZPS | 221 | 4.2646 | **0** | 0 (boundary) |
| BPAT | 465 | **19.8971** | 241 | 2.5194 |
| CISO | 63 | 3.1298 | 16 | 0.1482 |
| SRP | 198 | 4.1623 | **0** | 0 (boundary) |

**Critical interpretation correction:** the raw MH formula produces an OR=0 boundary value for AZPS and SRP nonwinter, because there are literally no nonwinter cold+high observations. This is neither a stable independently estimable interaction ratio nor evidence of protective causality. Accordingly the conventional winter/nonwinter OR ratio is marked **not estimable**, not calculated as infinity or with arbitrary 0.5 continuity correction. CISO's 16 such hours similarly yield unstable nonwinter resampling in some draws.

### Two ACTUALLY EXECUTED dependency robustness schemes

Both schemes run on original source and use exactly **2,000 draws each** (4,000 draws total). The same resampled year/month indices are used simultaneously for all BAs to preserve common shocks in descriptive BA comparisons.

1. **Whole-month clusters, within season:** independently resample all 30 Nov–Mar and 42 Apr–Oct year-month strata with replacement (seed `20261126`), preserving intra-month observed hour serial structure, but not dependence across months.
2. **Whole-year clusters:** draw six calendar years with replacement and retain all 12 months of each sampled year (seed `20261127`). Preserves within-year season dependence, with **only six distinct underlying annual clusters**. Its percentile intervals are sensitivity diagnostics, *not reliably calibrated publication confidence intervals*.

| Estimand | Monthly-block percentile 2.5–97.5% | Whole-year-block percentile 2.5–97.5% |
|---|---|---|
| AZPS winter MH OR | 2.50–6.93 | 2.88–5.90 |
| BPAT winter MH OR | **14.39–28.31** | **15.04–26.35** |
| CISO winter MH OR | 1.72–4.62 | 1.86–4.72 |
| SRP winter MH OR | 1.93–8.11 | 2.29–7.20 |
| BPAT nonwinter MH OR | 1.24–4.42 | 1.70–3.47 |
| BPAT winter/nonwinter OR ratio | 4.08–17.67 | 5.27–12.28 |
| BPAT vs AZPS winter OR ratio | 3.01–7.50 | 3.54–5.75 |
| BPAT vs CISO winter OR ratio | 3.82–11.95 | 3.42–12.95 |
| BPAT vs SRP winter OR ratio | 2.65–9.32 | 2.77–7.40 |

Original BPAT winter/nonwinter ratio of two descriptive MH ORs is 19.8971 / 2.5194 = 7.898; this ratio is *not a validated parametric interaction coefficient*. CISO winter/nonwinter bootstrap ratios use only nonzero nonwinter estimates (1,731/2,000 usable month-block draws); conditional intervals for them should NOT be interpreted like ordinary 95% CIs.

### Scientific admission status

This is compelling *exploratory* evidence for BA and seasonal heterogeneity under the selected data and definitions, **not statistical confirmation of effect modification, proof that geographic exposure is correct, or attribution of demand changes to climate change**. The original demand data includes source-vintage and spike concerns, 2025 was previously examined and is not blind, and BA-season cold anomalies may have very different physical meaning. With only six years, independent annual-cluster uncertainty is limited. Within-sample thresholds and candidate weather baseline are data-defined; event-level serial dependence and multiple explored hypotheses persist.

**C-1 remains frozen. C-2 historical weather attribution and SSP/PyPSA model-training gates remain closed.**

### Reproduction and archive

Actually executed Python programs:
- `c2_four_ba_season_interaction_bootstrap.py`
- `c2_four_ba_year_block_sensitivity.py`

Complete 4,000 draw CSVs, exact original 72-month source ZIP, full source SHA and results manifests, original cell counts, logs and README in verified local archive `C2_Four_BA_20261126_Season_Interaction_4000_Bootstrap_SourceLocked.zip` (SHA-256 **`6a10f4f4add9f771be4122d42bd210fb51366bb78d868191329eb27905cc959f`**, ZIP CRC verified). The GitHub repository stores exact aggregate results:
- `results/source_only/C2_FOUR_BA_2020_2025_SEASON_MH_EXACT_COUNTS_20261126.csv`
- `results/source_only/C2_FOUR_BA_SEASON_BLOCK_BOOTSTRAP_2000x2_SUMMARY.csv`

**Highest priority next:** source-validate historical BA weather spatial masks across all years; test BA×season relationship in a pre-specified inferential model with storm/event clusters and account for in-sample threshold creation. The separate actual PUDL respondent 21 FERC714 core-hour ingestion remains a crucial original-demand source gate.
