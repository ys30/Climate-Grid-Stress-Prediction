# C-2 E1 — Independent PUDL 2020–25 annual BA-county geography preflight (2026-11-24)

## Distinct pathway validated against official method

The PUDL service-territory compiler uses EIA-861 reported utility service counties and BA–utility associations to infer **annual** county-based balancing-authority support and optionally GeoParquet polygons. This is an independent geography *candidate* from the CEC 1305/1306A reporting pathway and from frozen 2018 HIFLD control-area candidate masks. See official [PUDL v2026.10.0 source documentation](https://docs.catalyst.coop/pudl/en/v2026.10.0/autoapi/pudl/analysis/service_territory/index.html).

## Executed deliverable, not verified external data

A complete standalone ZIP was generated locally: `C2_PUDL_Historical_BA_Geography_Source_Gate_2026_11_24.zip`, SHA-256 `99627ddfb13134988ff0fc5406ab305b25f7959b4b3115c495fbbd2a33cab362`. Contains:

- `c2_pudl_ba_county_vintage_gate.py`, source-only validator requiring a SHA-pinned reviewed EIA-861-derived BA/year/county CSV and fixed PUDL release;
- `test_c2_pudl_ba_county_vintage_gate.py`, **8/8 local tests actually passed**, using only synthetic fixtures;
- `README.md`, input source contract and strict study-admission restrictions.

The program rejects missing cohorts, duplicate BA-year-counties, non-FIPS county IDs, unpinned source identity, changed file bytes, and invented operational-boundary authority. It requires exactly 24 annual BA source cohorts (AZPS, BPAT, CISO, SRP × 2020–25). It computes annual county counts, added/removed *source associations*, and annual Jaccard overlap. A county added or removed is **not classified as a real BA control-boundary change** absent independent corroboration. It never estimates hourly customer/load weights or permits model training.

**Crucial status:** no independent original PUDL GeoParquet/file was newly retrieved or processed in this turn; no actual county counts or boundary changes for these 24 cohorts are reported here. Previous separately audited historical EIA-861 associations remain source evidence, not a proof of complete geographic load attribution. This report indexes locally delivered tested code and is not a claim that the ZIP was uploaded into GitHub repository.

## Next empirical task

Obtain authentic version-pinned annual PUDL BA service-county GeoParquet or reproducible PUDL source extract for 2020–25, validate BA ID mappings and year-specific reporting coverage, export original BA/year/county FIPS plus SHA manifest, then run the included validator and compare to already reviewed HIFLD/TIGER proxies. Cross-check year changes against dated CEC 1305 data when accessible.

Historical BA **operational** footprint and **load-weighted hourly** geography are not approved. EIA-930 source-vintage conflicts, AZPS2023 canonical source failure and already-explored 2025 data remain research restrictions. No formal prediction, climate attribution, SSP projection or PyPSA grid stress model result was produced. **C-1 frozen.**
