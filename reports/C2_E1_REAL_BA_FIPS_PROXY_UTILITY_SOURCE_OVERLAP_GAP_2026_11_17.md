# C-2 E1: empirical BA county FIPS proxy vs utility-source geography risk (2026-11-17)

## Source integrity and limitations

Two previously obtained real EIA-861/PUDL source datasets were combined. First: the BA county service-territory FIPS list originally extracted from **PUDL nightly**, not an immutable tagged release; frozen GitHub artifact **14134338768**, member `2020_2025_EIA861_fourBA_yearly_county_FIPS_memberships_UNAPPROVED.csv`, SHA256 `6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68`, 1,110 six-year rows. Second: immutable prior actual EIA-861 association bridge artifact **14144934238**, member `EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv`, SHA256 `957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`, 1,418 six-year records.

Both are checked before use; only 2020–2023 analyzed. **Freezing a downloaded nightly artifact is not equivalent to pinning the upstream original release vintage**. BA-level county membership is NOT official historical BA polygon, and utility–county reporting membership is NOT load allocation.

## Actual 2020–2023 empirical outcomes

| BA | BA source counties, each of 4 years | Annual utility–state links, summed over 4 years | Links with no utility county source | Links with multi-BA utility association | Links with excluded out-of-state counties |
|---|---:|---:|---:|---:|---:|
| AZPS | 15 | 96 | 48 | 17 | 0 |
| BPAT | 109 | 443 | 7 | 0 | 88 |
| CISO | 58 | 361 | 207 | 6 | 10 |
| SRP | 3 | 33 | 25 | 17 | 0 |

The **exact FIPS sets**, not merely the county counts, are constant for each BA between 2020 and 2023 in this frozen nightly extraction. That fact by itself is NOT proof of real historic BA boundary stability. Furthermore, all **three SRP source counties are also in AZPS's 15**, i.e. 100% of SRP's source counties, 20% of AZPS's source counties, are shared, and remain so in all four years; the other five pairwise BA FIPS intersections are zero. This explicitly refutes treating these county unions as a **mutually exclusive partition** for BA load allocation. A county can have customer meters in different BA service territories.

CISO's 207 / 361 utility-year/state source links without county evidence and BPAT's 88 / 443 with cross-state county exclusions show that broad BA FIPS memberships cannot validate utility-specific weather exposure. AZPS/SRP's 17+17 multi-BA source associations are per-year overlapping source *links* (not independent utility counts or MWh). No hourly EIA-930 load has been spatially localized.

These are **source association counts**, not utility populations, county-level load fractions, or missing MWh. Do NOT use the fractions 207/361, 25/33 etc. as load missingness percentages.

## Independent reproduction

`src/c2_e1_real_BA_county_proxy_vs_utility_links.py` requires both original member SHA256, correct expected row counts, reject source flags pretending source proxy is model-ready, strict BA FIPS sets and SRP/AZPS 3-FIPS overlap. Tests: `tests/test_c2_e1_real_BA_county_proxy_vs_utility_links.py` cover fail-closed invalid source inputs and approval guard. Workflow `.github/workflows/e1-ba-county-fips-vs-utility-source.yml` downloads both original archived artifacts and writes 16 BA-year source comparisons, 24 BA-pair-year intersection rows, four-BA risk summary and source-only provenance JSON.

Successful [GitHub Actions run 44227147645](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44227147645), artifact **14392159503**. This is a source-only research diagnostics result and **not evidence of a successfully passed E2 geography model admission gate**.

## Decisive scientific next step

Before any E2 weather–load model: acquire *release-pinned*, historically relevant, **utility-to-county FIPS membership by year** and preferably county-allocated **actual retail MWh, customers, or defensible explicitly verified service territory allocation**, along with verified BA operating boundary vintage and mixed utility/BA overlap treatment. Match each utility's reported MWh to verified county weights, explicitly sum and compare to annual total; validate exposure under multiple nonexclusive geographic alternatives. Do not infer load from county counts or source union. Holdout protocol is an independent gate.

`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`; `GEO_LOAD_RELEVANCE=BLOCKED`; `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`; `model_training_permitted=false`. C-1 frozen and 2024–2025 sealed hourly demand untouched.
