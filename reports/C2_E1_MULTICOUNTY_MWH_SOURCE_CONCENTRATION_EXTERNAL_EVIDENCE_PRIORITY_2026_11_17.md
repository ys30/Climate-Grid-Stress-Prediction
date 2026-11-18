# C-2 E1 — Observed multi-county retail source concentration and external evidence priorities (2026-11-17)

## Purpose and boundaries

This is **NOT** county-specific electric load, model training, a true BA operating-area map or identification of county MWh fractions. It ranks utility-level source entities by their **actually observed 2020–2023 annual retail MWh that are geographically ambiguous** because the same utility reports two or more service county FIPS. An independent utility-specific county customer/meter/MWh allocation could in principle resolve some, but a service area polygon alone does not establish electricity consumption shares.

Actual source: independently verified original PUDL **v2026.10.0** annual Sales SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`; verified 933-row year/utility/state/BA FIPS source from tag-pinned `core_eia861__yearly_service_territory.parquet`. Input GitHub artifact **14400293606** from successful run [44244205677](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44244205677) — source utility actual MWh member `C2_E1_UTILITY_MWH_ACTUAL_AND_COUNTY_SUPPORT.csv`, SHA256 `05d0a092e2508d0fa8b092ae20faeca9f0b2c07859d9b96e165eddc3c0b79cbb`; independently verified 16 BA-year source totals member SHA256 `d5cff3454db19781f0aa38eb034b8aae2d81d6c37541f9f43b67721b52870681`.

## Original four-year empirical source concentration

| BA | Original observed multi-county retail MWh (2020–2023) | Number of multi-county utility×state sources | Top-1 share of ambiguous-source MWh | Top-3 share | Top-10 share |
|---|---:|---:|---:|---:|---:|
| AZPS | 120,464,912 | 1 | **100.00%** | **100.00%** | **100.00%** |
| BPAT | 123,932,777 | 36 | **21.49%** | **44.15%** | **68.35%** |
| CISO | 389,552,906 | 6 | **56.29%** | **98.95%** | **100.00%** |
| SRP | 123,741,352 | 1 | **100.00%** | **100.00%** | **100.00%** |
| **Total** | **757,691,947** | **44 BA-utility-state source combinations** | | | |

Source utility IDs and cumulative ranking: **AZPS: ID 803 (AZ)**, alone 100% of AZPS ambiguous-source MWh; **SRP: ID 16572 (AZ)**, alone 100%; **CISO: ID 17609 (CA)** ~56.29%, **ID 14328 (CA)** ~32.88%, **ID 16609 (CA)** ~9.78%, top 3 ~98.95%; **BPAT: ID 17470 (WA)** ~21.49%, **ID 19325 (OR)** ~17.46%, **ID 1738 (WA)** ~5.21%, top 3 ~44.15%. This is merely a ranked source evidence acquisition queue. Do not infer that original ID equates to a single independent BA customer delivery footprint. All values use observed annual bundled sales and explicit source multi-county classification, not electricity meters by county.

## Why top-k has limited meaning

If an externally independently checked county MWh allocation becomes available for all top-k source entities, the percentage above is an **upper bound on which ambiguous-source MWh would enter scope for resolution**. Obtaining a map, customer count by county, population share, or NLR modeled population-distributed hourly county profiles **does not guarantee** a known fraction of electric MWh becomes identified. The true reduction in unidentified county MWh may remain zero.

Do not add sources across BA without handling nonexclusive actual source reporting. Source-focused panel records are disambiguated BA, utility ID, state and year; multigeography source records in the ranked input have no flagged multi-BA source overlaps, but utility identity should still be checked before applying operational BA assumptions.

## Reproduction and scientific guard

New deterministic SHA-enforced script `src/c2_e1_real_multicounty_source_evidence_priority.py`, regression tests `tests/test_c2_e1_real_multicounty_source_evidence_priority.py`, workflow `.github/workflows/e1-real-multicounty-source-priority.yml`. The program checks that original observed multi-county MWh by BA equals the independently verified real source annual MWh totals, sorts utility/state candidates, preserves annual changes, emits top-1/2/3/5/10 fractions, and refuses flags for verified county allocations. The new [GitHub Actions run 44246310413](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44246310413) was queued at first report publication; update its observed result before claiming CI success.

Official county-level modeled external benchmark NLR `HistoricalLoadData` is **population-allocated** and BA-load-informed: https://data.openei.org/submissions/8562 . It does **not** independently validate county actual electric demand.

Geographic gate results still `GEO_LOAD_RELEVANCE=BLOCKED`, `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`, `model_training_permitted=false`. C-1 frozen; 2024–2025 EIA-930 demand holdout unopened.
