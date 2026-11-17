# C-2 E1 — VERIFIED real EIA-861 annual retail sales geographic-source coverage (2026-11-17)

**Major empirical milestone. Two successful GitHub Actions artifacts downloaded and independently reprocessed; no fitted models. C-1 frozen.**

## Source and independent replication

**Do not confuse this work with the earlier synthetic sales coverage tests.** Public PUDL v2026.10.0 original `core_eia861__yearly_sales.parquet` was downloaded in completed GitHub Actions run [44032717255](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44032717255), artifact **14304894732**, with all data retrieval, SHA, annual join and artifact-upload steps showing **success**. Independently, another completed successful run [44031912206](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44031912206), artifact **14305906742**, yielded **byte-for-byte identical annual summary and source-association-detail CSVs**. The official PUDL Parquet SHA256 in *both* results is:

`996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`

The frozen existing source bridge inner CSV SHA256 remains `957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef`. Both successful result CSV SHA256 values:
- 24-row annual sales: `2b437b6288e1d8221aa555c63aadfbf16d033406b4ac5ee6c70bff0d497987c0`.
- 60-row source-association-detail: `48a69bed00dcbcaae59b8d67b132d17f78e1e8c2db3d3c9fcd120ea288ffc9dd`.

**Official upstream records:** 413,260; records within the 4 BA × 2020–2025 scope: 5,180; source-selected observed *bundled* / non-`total` class records with nonmissing sales MWh: **2,224**. Source selection excluded 350 not-observed, 1,285 non-bundled, and 1,321 with missing MWh (sequential exclusions). Four BAs × six years **24/24** have nonempty selected annual sales MWh. This source was *first observed* rather than historically pre-pinned, but after observing identical Parquet SHA across two independent runs, commit `64d4b96e7d0b9a546cfa98627aa247d29e8c20db` pins this SHA in future workflow runs; next CI result must be checked separately.

## Actual energy-weighted county-source coverage, 2020–2023 training + validation period

| BA | Selected observed bundled MWh | Strict county-source-matched MWh | Matched share | Multi-BA utility association MWh | Other unmatched MWh | Complete matched customer-years share |
|---|---:|---:|---:|---:|---:|---:|
| AZPS | 129,057,618 | 125,305,605 | **97.0928%** | 3,379,675 | 372,338 | 95.2086% |
| BPAT | 207,663,786 | 207,661,094 | **99.9987%** | 0 | 2,692 | **unavailable**, BPAT 2022 customer aggregate incomplete |
| CISO | 463,195,807 | 447,276,180 | **96.5631%** | 12,405 | 15,907,222 | 94.3141% |
| SRP | 124,284,031 | 123,741,352 | **99.5634%** | 542,679 | 0 | 99.2085% |

The energy-weighted share is computed as the **sum of strict county-source-matched eligible reported MWh divided by sum of all selected reported MWh** over these four calendar years (not the arithmetic mean of annual percentages). Customer-year sums (if complete) are descriptive sum of annual customer counts, **not distinct customers across years**. The annual report confirms BPAT 2022 and 2025 customer coverage is incomplete; do not impute missing customers as zero.

## Year-specific evidence and implication

- CISO strictly matched sales share fell from **97.3504% in 2020** to **95.4638% in 2023** and **95.1600% in 2025**, although raw association-key match fraction over six years is only ~42.9%. These are very different denominators; low match fraction by utility source count cannot infer low energy-weighted coverage.
- AZPS has about **2.62%** selected training/validation MWh in nonexclusive utility–BA–state source links; these are not counted as strictly matched. SRP has ~0.44%, CISO ~0.0027%.
- BPAT's near-100% selected MWh coverage does **not** resolve excluded cross-state service-territory county slots or certify actual demand locations.

## Methodological restrictions and next gate

The verified ratio is **the proportion of selected observed bundled retail MWh attached to a BA–utility–state association that has a county source**. It does NOT measure the fraction of actual **hourly BA net demand**, utility meter positions, customers' county allocations, climate weather exposure, or independent true operating BA polygon. In particular source table `core_eia861__yearly_sales` does not itself give a within-utility/county spatial split. Business models and service types may differ in reporting coverage; excluded 1,321 missing-MWh rows limit generality.

2024–2025 rows were independently read as **annual sales-source metadata**, but 2024–2025 *sealed hourly demand test* observations were not used for fitting, anomaly threshold selection or model evaluation.

Scientific gates still fail: `GEO_HISTORICAL_BA_FOOTPRINT` and `GEO_LOAD_RELEVANCE` are **not cleared** solely by annual sales association, `LOAD_QUALITY_HOLDOUT_PROTOCOL` remains blocked, and `model_training_permitted=false`. C-1 remains frozen. To move E1→E2: resolve county-level utility sales allocations (or independent validated metered load geography), report missing/total sales and source asymmetries, then review explicit spatial estimand.

## Third (SHA-pinned) empirical run and full CI repair confirmation

After the first two independently verified downloads, the true PUDL parquet SHA256 `996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe` was frozen as the default in workflow commit `64d4b96e7d0b9a546cfa98627aa247d29e8c20db`.

- [SHA-pinned source acquisition and real sales join run 44037370237](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44037370237) completed **successfully**; resulting artifact **14307004376**. This third artifact contains **no** `NOT_YET_PREPINNED.txt`; the workflow compared retrieved source content with its preexisting fixed SHA.
- Both output CSVs in the pinned artifact are **byte-identical** to the prior two runs: 24-row source selected annual summary SHA256 `2b437b6288e1d8221aa555c63aadfbf16d033406b4ac5ee6c70bff0d497987c0`; 60-row source classification detail SHA256 `48a69bed00dcbcaae59b8d67b132d17f78e1e8c2db3d3c9fcd120ea288ffc9dd`.
- The unrelated full `phase1-ci.yml` test suite had been failing with **2 errors among 154 tests**: tests/test_temporal_gate.py omitted the newly required `observed_keys`, `valid_values`, and `blank_or_invalid` input fields. Commit `5a38ff9b3ece32b1767a5b6b4b101e4fb0f23365` repaired the **synthetic test fixture** rather than weakening strict EIA-930 coverage input checks. [CI run 44037329404](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44037329404) **passed**, as did the full [CI run 44037370218](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44037370218) on the pinned-source workflow commit.

**Therefore:** both the newly measured annual sales source coverage and the full source-contract CI can now be described as **verified successful**, not 'pending Actions'. This does **not** certify within-county utility customers, historical operational BA load location or formal E2 model admission. Those scientific gates remain blocked.
