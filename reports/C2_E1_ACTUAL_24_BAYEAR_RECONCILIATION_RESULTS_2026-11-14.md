# C-2 E1 — Independently recomputed actual 24 BA-year county-source comparison

Date: 2026-11-14 Mountain (2026-11-15 UTC).
Status: **SOURCE-LEVEL COUNTY SET RECONCILIATION COMPLETE; MODEL TRAINING BLOCKED.**

## Actual evidence and method
Downloaded the two original, successfully completed GitHub Actions artifact ZIPs and checked archive digests:
- frozen BA annual counties: run 43647297586; artifact 14134338768; ZIP SHA256 `c063bd251d633344ffb58944ded15e17fb6062c48518987690ec9161d6c5d87f`.
- corrected state-scoped BA–utility–county bridge: run 43672928429; artifact 14144934238; ZIP SHA256 `0e3d5ac5556b155456deb79bbb78be4b707907043764faca29edf1552721385e`.
- frozen 1,110-row BA-year/county input CSV SHA256 `6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68`.
- utility bridge source CSV SHA256 `e70ac12859b47e24d07cff76201e85a33d3f6c4701e040ed0ea453e00f3e03dc`.

An independent local Python recomputation read the original CSVs from the two archives. It rejected duplicate BA-year/source county identities, verified 24 required BA-year slots, validated FIPS identifiers and set containment, and reconciled all 1,418 association rows and 439 unmatched associations with the archived upstream JSON. The full 24-row CSV, audit JSON, human-readable report and reproduction script were packaged separately for the conversation.

## Verified results

| BA | Frozen counties/year | utility association rows | Matched | Unmatched | Match rate | Exact county-set matches | Jaccard each year |
|---|---:|---:|---:|---:|---:|---:|---:|
| AZPS | 15 | 146 | 72 | 74 | 49.3151% | 6/6 | 1.0 |
| BPAT | 109 | 670 | 659 | 11 | 98.3582% | 6/6 | 1.0 |
| CISO | 58 | 550 | 236 | 314 | 42.9091% | 6/6 | 1.0 |
| SRP | 3 | 52 | 12 | 40 | 23.0769% | 6/6 | 1.0 |
| **Total** | — | **1418** | **979** | **439** | **69.0409%** | **24/24** | **1.0** |

For all 24 BA-year pairs (2020–2025 × AZPS/BPAT/CISO/SRP), the corrected state-limited utility-county FIPS set equals the frozen BA-county source FIPS set exactly: zero additions, zero omissions, 24/24 Jaccard=1.000000. All 24 groups nevertheless contain one or more utility-state associations lacking a matched service-county row. The unrestricted source union has extra unique out-of-state counties in BPAT (5–15/year); strict state-limitation is necessary.

## Interpretation and limitations
1. **This is administrative source-set agreement within the PUDL/EIA-861 lineage, not independent external BA geography validation.** The two constructions can share upstream logic or data. Jaccard=1 does not justify describing the geographic proxy as a physical BA operating perimeter.
2. **69.04% is an association-row coverage fraction, not percent of customers, county residents or MWh.** Missing association counts do not measure the actual amount of missing load.
3. These annual service-county sets are not observed utility customer load weights or hourly BA electricity exposure. Overlapping BA/utility relations cannot be forcibly partitioned without evidence.
4. The calculation was performed independently on downloaded archived evidence, **not** claimed as a completed downstream GitHub Actions reconciliation. The downstream workflow's live run status is still unverified.
5. The scientific blockers `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, and `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain open. `model_training_permitted=false`. No E2 GAM/XGBoost forecast skill, anthropogenic attribution, or E3/E4 SSP/PyPSA stress result is established here.

## Immediate research consequence
The narrow *source consistency* question is answered and should not be endlessly re-tested: **24/24 source county sets agree**, but source coverage and scientific geography/load-weight identification remain unresolved. Prioritize independent spatial load relevance and complete EIA-930 × ERA5 longitudinal panel QA. Keep C-1 frozen.
