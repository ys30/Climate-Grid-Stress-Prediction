# C-2 E1 — Exact version-pinned utility county FIPS lineage, 2020–2023 (2026-11-17)

## Objective

Replace a previously downloaded PUDL nightly BA county union/count proxy with real individual utility county FIPS source rows from *fixed PUDL v2026.10.0*. Report original service territory source completeness, utility-to-BA non-exclusivity, historical temporal changes and geography admission gaps. No E2 model training or BA demand-to-county allocation.

## Pin and provenance

- Original public PUDL v2026.10.0 `core_eia861__yearly_service_territory.parquet` (S3 `s3://pudl.catalyst.coop/v2026.10.0/`); **original raw file SHA256 `3d6c4cc54bd856e678fa0b3eb162e2c8867a3fbe64dfae8f862f0dd82cca0605`**.
- Original independently frozen PUDL BA–utility–state association inner CSV SHA256 `957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`, 1,418 source records spanning 2020–2025, **933** in 2020–2023.
- Source-only code `src/c2_e1_pudl_2026_10_utility_county_fips_original.py`, synthetic tests `tests/test_c2_e1_pudl_2026_10_utility_county_fips_original.py`, workflow `.github/workflows/e1-pinned-utility-county-fips-original.yml`.
- Actual pinned data [GitHub Actions run 44228454642](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44228454642) **SUCCESS**, artifact **14393473675**, downloaded and independently evaluated; 933 original year–BA–utility–state–FIPS set records, 17 nonexclusive source utility–state–year groups, 4-BA summary, pinned SHA256 provenance.

## Source completeness facts

| BA | Year–utility–state links (2020–2023) | With at least one original county FIPS | With no original county FIPS | Nonexclusive BA utility link rows |
|---|---:|---:|---:|---:|
| AZPS | 96 | 48 | 48 | 17 |
| BPAT | 443 | 436 | 7 | 0 |
| CISO | 361 | 154 | 207 | 6 |
| SRP | 33 | 8 | 25 | 17 |
| **Total** | **933** | **646** | **287** | **40** |

**Every one of the 933 original county counts reconciles exactly to the original version-pinned county FIPS list**; any county-count mismatch raises a hard failure. The 40 nonexclusive **link rows** arise from **17 unique year–utility–state associations**, including triple-BA cases. The **17/17 nonexclusive source groups contain zero county FIPS in this actual territory table**. This is evidence of *absence of county-source allocation* for these groups, not evidence of zero retail MWh or absence of actual electricity customers.

These are counts of source reporting relationships, not BA electricity-consumption shares, customer counts, or number of whole utilities.

## Exact historical county FIPS changes

A separate reproducibility inspection of the downloaded 933-row output compared FIPS sets within complete 4-year BA–utility–state entities. AZPS/BPAT/SRP have **zero** changed FIPS sets in their complete four-year entities; CISO has **two**:
- **CISO utility 16612, CA**: 2020 and 2021 `06075` (San Francisco); 2022 and 2023 `06075;06081` (San Francisco and San Mateo).
- **CISO utility 61432, CA**: 2020 `06053;06069;06087` (Monterey, San Benito, Santa Cruz); 2021 **none recorded**; 2022 and 2023 `06053;06069;06079;06083;06087` (also San Luis Obispo and Santa Barbara).
- No full-four-year utility entity has a different FIPS set with *unchanged reported county count* in this original panel. That does NOT prove source county membership physically stable.

CISO has 207/361 year-link rows with no original county source; AZPS 48/96 and SRP 25/33 are also unresolved. BPAT 7/443 have no county source, but its independent cross-state exclusions and valid historical geography still require audit.

## Scientific interpretation

The result upgrades **utility-reported FIPS-source traceability** from nightly proxies to the *tagged* original PUDL release; it does **not** authorize `GEO_HISTORICAL_BA_FOOTPRINT`. EIA-861 utility service territory may span multiple counties and have no metered energy allocations to any county. If county rows are absent, neither weights nor estimated county MWh should be created by populating BA-level unions.

The AZPS/SRP BA county union source overlap does not by itself prove electricity load double count; the multi-BA utility-linked county source records have no FIPS and cannot be spatially resolved using that source alone. Any future load-relevance gate must require actual county-specific electricity consumption or validated customer/meter location weights plus a check of nonexclusive BA loads. Zero missing county-source records ≠ load coverage.

**All three admission gates remain BLOCKED**: `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL`. `model_training_permitted=false`, C-1 frozen, sealed 2024–2025 EIA-930 hourly demand not used.

## Next decisive source test

Check whether original year-tagged EIA-861 county-level retail electricity sales or customer counts exist at a utility/county granularity. If not, document unidentifiable allocation fractions and conduct strictly *unapproved sensitivity* comparisons of uniform county, county population, and reported service geography alternatives with no E2 fitting; use BA historical boundaries from an authoritative versioned source for scientific admission, not county unions.
