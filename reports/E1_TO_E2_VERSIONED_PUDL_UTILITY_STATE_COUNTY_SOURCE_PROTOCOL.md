# C2 E1 → E2: BA–utility geographic relevance and strict audit status

Date: 2026-11-14 Mountain / 2026-11-15 UTC. **C-1 remains frozen.**

## Verified data lineage (not equivalent to geographic model authorization)

Independent actual PUDL versioned-source evidence for EIA-861 balancing authority annual county sets is **SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43669704182 .

- The two immutable input source object hashes from tagged PUDL v2026.10.0 are SHA256:
  - `core_eia861__yearly_balancing_authority.parquet`: `0fdb3930b3fbec15845242d1fbd96182bc015dfaf9ba23a04ebb646886d9ea4d`.
  - `out_eia861__yearly_balancing_authority_service_territory.parquet`: `a50f78de5c7a70ec510a9de241872955e737d73e15a48842ede80c5c610b6791`.
- 24/24 source BA-year identity matches and 24/24 source county-membership-set matches against the SHA256 frozen older nightly-derived snapshot; zero observed differences.
- This evidence resolves the *specific EIA861 county snapshot upstream release-provenance gap*. It does **not** validate an operating BA region, customer geography or electricity load allocation.
- Existing population-area C source has 182 official county Census 2020 estimates-base records and a distinct complete trace to its fixed weight CSV; 2,688 independently audited real ERA5 A/B/C source BA-hours remain unmodified. Archived source gate: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43669567273 .

## Why BA–utility association needs the PUDL state-limited join

Official PUDL's historical geographic inference identifies utility–county territories and **BA–utility–state** associations. Its documented `get_territory_fips(..., limit_by_state=True)` applies the BA association state to avoid collecting utility service counties in other states as BA counties.

Reference: https://docs.catalyst.coop/pudl/en/v2026.10.0/autoapi/pudl/analysis/service_territory/index.html

The new code `src/c2_eia861_ba_utility_county_probe.py` uses:
- `core_eia861__assn_balancing_authority.parquet` for `(report_date,balancing_authority_id_eia,utility_id_eia,state)`;
- `core_eia861__yearly_service_territory.parquet` for `(report_date,utility_id_eia,county_id_fips,state)`;
- tag-pinned original Parquet SHA256 outputs; 2020–2025 four BA identity checks; unmatched BA–utility–state associations; ambiguous utility-year-state relationships associated with multiple BAs.
- Actual county membership only where `year`, `utility_id_eia` **and state** match, with unrestricted union of source utility counties as an **overcoverage diagnostic**.
- No artificial exclusive partition for overlapping SRP/AZPS or other utility associations.

**This is a linked utility service-COUNTY proxy only**. A utility's annual territory geography does not reveal where its customers, hourly peak demand, or demand-serving boundary of the balancing authority lie inside a county. Neither customer count, usage volume, nor transmission-zone allocation is inferred from the existence of a county row.

The original and corrected version of the utility bridge workflow were both submitted. Most recent corrected run:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43670963932 .

At writing that corrected CI was **QUEUED**. Its actual annual utility counts, missing county links, ambiguous utility-BA assignments and source Parquet digests are NOT verified; they must be read from a successful actual run before becoming reported findings.

## E1 → E2 scientific admission: separate conditions

1. **Raw source and version checks**: 2,688 source-only A/B/C matched ERA5 BA hours confirmed; official Census raw county population file hashed; EIA861 original source v2026.10.0 24-year-BA county identity sets confirmed. The updated machine gate that independently verifies every versioned county membership, before marking the release source blocker cleared, is submitted as https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43670320754 and is **not yet CI-confirmed**.
2. **Historical BA spatial exposure validity**: unresolved, especially HIFLD repaired 2018 geography and EIA861 whole-county support. No official six-year operating BA geometry certified.
3. **Load-relevant spatial estimation**: unresolved. County resident population C does not represent utility meter counts. Utility-to-BA links are a necessary diagnostic, **not sufficient** for electrical load weighting. A prospective new proxy D must transparently state its weight basis (e.g. customer counts or county-reported retail electricity), its crosswalk uncertainty and sensitivity.
4. **Original demand QA and chronological test**: preserve 260 original EIA930 missing-demand hours and 70 source anomaly candidates. No silent imputation, accidental duplicate BA electric load, ad hoc anomaly deletion, or post-hoc hyperparameter tuning on 2024–2025 sealed holdouts.
5. **Formal E2 modeling**: still **BLOCKED**. No validated cross-year GAM/XGBoost, ALL/NAT anthropogenic climate attribution, CMIP6 SSP scenario or PyPSA future stress run exists merely from weather proxy support sensitivity.

Scientific priority after the source bridge CI: quantify utility relationship coverage and mapping ambiguity **by BA and year**, compare it with the already frozen annual BA county sets, then decide whether any proposed geography/utility weighting is supportable. Do not automatically prefer C or utility-union proxies without independent load-related verification.

C-1 remains unchanged.


## Latest execution status: amended E1→E2 gate source audit has now PASSED

The latest version-aware E1→E2 audit job **SUCCESS**:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43670320754 .
The newest frozen-source gate artifact is:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43670320754/artifacts/14144762435 ,
GitHub archive SHA256 `428f82144297baa1c4041fb0185207aa171ec336bf1e271f7c88f82e2ba5267f`.

Original 2,688 actual ERA5 A/B/C observations, official Census population sources, all **1,110 yearly BA–county memberships**, and original versioned PUDL `v2026.10.0` source Parquet SHA256 hashes were independently checked. The tagged-original membership output and prior old-nightly-derived source exhibit exact BA-year, BA-code, source ID and county membership identity. The source provenance gate **`PROVENANCE_PUDL_RELEASE` = CLEARED**; other three gates `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE` and `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain OPEN/BLOCKED. Consequently `model_training_permitted=false` is unchanged.

### State-limited utility county matching and direct frozen BA source comparison

A separate utility-to-BA source link was first demonstrated against actual original PUDL v2026.10 Parquet `core_eia861__assn_balancing_authority` SHA256 `837b4f62e740a501ad8f0b96a3b7d8597fa888cf7ad516d0401cb284ab0f8ef0`, and `core_eia861__yearly_service_territory` SHA256 `3d6c4cc54bd856e678fa0b3eb162e2c8867a3fbe64dfae8f862f0dd82cca0605`. **The earliest original CI pass used an overly broad cross-state union, so do not treat its county union counts as the state-limited answer.** The final source investigation limits `(year,utility,state)` on both sides, in line with PUDL service-territory's `limit_by_state=True` concept.

New source diagnostics include exact semicolon-delimited county FIPS of each 24 BA-year state-limited utility union, and separately the unrestricted utility-county FIPS union for quantifying cross-state inflation. The utility-association audit explicitly records missing utility/state territory rows and multivalued BA associations, without declaring customer-level load distributions.

Independent `src/c2_eia861_utility_BA_source_comparison.py` and workflow
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/workflows/e1-PUDL-utility-vs-BA-county-source-audit.yml
check **exact** utility-versus-BA county FIPS set intersection, additions, removals and Jaccard for 24 BA-year slots, using the previously frozen membership file SHA256. This is a new source geometry DIAGNOSTIC, never an authorized BA operating region or load-weighted temperature predictor.

The latest corrected state-limited utility source CI is
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43672928429 .
**At this report update it remained queued**, and the independent utility-to-frozen-BA county reconciliation had not completed. Do not assert any completed state-limited BA-by-year utility coverage, Jaccard or model acceptance until these CI runs succeed and their original artifact hashes are inspected.

C-1 frozen; C-2 modeling gate CLOSED.
