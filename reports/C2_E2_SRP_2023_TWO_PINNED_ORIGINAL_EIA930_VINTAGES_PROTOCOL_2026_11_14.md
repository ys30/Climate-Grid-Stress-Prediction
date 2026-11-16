# C2 E2 — Pinned raw EIA-930 SRP February 2023 historical-vintage comparison protocol

Date: 2026-11-14 Mountain. C-1 is frozen. **Result pending original ZIP fetch; E2 training blocked.**

## Newly verified external evidence
Catalyst Cooperative's Zenodo/PUDL EIA-930 original data package provides two date-separated archived raw 2023-H1 EIA-930 ZIPs:
- **2025-11-23 v53.0.0**: https://zenodo.org/records/17688027 , `eia930-2023half1.zip` MD5 `122e5d253321b7baef657a4880f9a579`.
- **2026-09-01 v92.0.0**: https://zenodo.org/records/22215263 , `eia930-2023half1.zip` MD5 `1b4acef4e1ec596cf92e7658f9be64c7`.

This proves archived ZIP bytes differ; it does **not** establish that the specific SRP demand hours differ, that EIA officially corrected them, or that either is accurate. EIA itself notes reporting revisions and advises caution with unadjusted BA hourly data: https://www.eia.gov/electricity/930-content/about.html .

## Newly implemented reproducible verification (GitHub)
- `src/c2_srp_eia930_raw_vintage_compare.py`: downloads pinned ZIPs, checks original MD5, extracts only `*-balance.csv`, reads `SRP` actual `Demand (MW)`, translates original UTC hour-ending labels to UTC interval-start and compares 11 fixed hours from 2023-02-26 20:00Z through 2023-02-27 06:00Z.
- `tests/test_c2_srp_eia930_raw_vintage_compare.py`: synthetic tests of hour-ending alignment, changed values, identical values and duplicate-hour failure.
- `.github/workflows/e2-srp-eia930-vintage-comparison.yml`: on push or dispatch, runs tests and the pinned real-source comparison; emits per-hour CSV, JSON provenance and GitHub Actions summary. Real run success and row-level revisions **are not confirmed** by writing this file.

The baseline project's actual original EIA-930/ERA5 source reports SRP original values at 2023-02-26 22:00,23:00 and 2023-02-27 00:00,01:00,02:00 UTC interval start as 2,958; 68,520; 45,097; 27,030; 3,578 MW. The two central extreme hours were not flagged by the original 70-hour source screen but were independently flagged by two follow-up local-median screens. The raw data must not be silently corrected or dropped.

## Scientific interpretation rules
1. Distinguish archive byte difference, actual source-hour revision across vintages, and independently verified reporting error. They are NOT equivalent.
2. Even if the value changes between published vintage ZIPs, use the exact difference, time label and source provenance to investigate—not as automatic permission to remove observation.
3. Preserve training=2020–2022, validation=2023, held-out=2024–2025. The new vintage audit examines the 2023 validation source event only, not 2024–2025.
4. Original 2018 HIFLD vs county-area vs county-population ERA5 proxy comparison remains scientific sensitivity, not approved BA demand exposure. `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, and `LOAD_QUALITY_HOLDOUT_PROTOCOL` remain BLOCKED; `model_training_permitted=false`.

## Immediate decisive output
Obtain successful `e2-srp-eia930-vintage-comparison.yml` artifact with 11 original hour-ending records from both historical vintages, archive SHA256 and changed-hour count. Without that artifact, the retrospective source-correction question remains OPEN.

## November 14 follow-up: archive-member identity and three-level revision QA

Both dated Zenodo ZIP previews independently confirm three members: `eia930-2023half1-balance.csv` (42.0 MB uncompressed), `eia930-2023half1-interchange.csv`, `eia930-2023half1-subregion.csv`. Therefore the `*-balance.csv` selection in the repo is grounded in the actual archive structure rather than guessed.

The comparison now records each original ZIP SHA256 **and each uncompressed original Balance CSV SHA256**, plus per-hour SRP original demand equality and source QA. This separates:
1. **ZIP byte changes** (documented by distinct official archive MD5) — do not prove input CSV changes;
2. **Raw Balance CSV changes** (must check extracted CSV SHA256) — do not prove target-hour SRP revisions;
3. **SRP target-hour demand value changes** (only counted after matching original UTC hour-ending labels).

Expanded synthetic regression tests cover changed raw values, unchanged raw values, duplicate UTC keys, incomplete SRP hour coverage, and archives with distinct metadata but identical raw Balance CSV. The original four-test standalone Python protocol suite was rerun locally and passed 4/4; the new GitHub regression tests and workflow **have not yet returned verified run results**. An independent ZIP/inner-file-hash synthetic edge-case check also passed locally.

These enhancements were committed in GitHub commits `4068a0d9723c86a94925b74133f5021479025d65`, `4cada625581939a7f1840ef562e513ef106e2bbb`, and `e3e58e46aa9003ed67ee9a7ba019f8dcb6c491ff` (workflow summary formatting fix). The direct external 19.5 MB ZIP download could not be completed in this session, and latest Actions result cannot be established via current connector. Thus **no verified SRP cross-vintage numerical change claim is made**. Gate unchanged: `model_training_permitted=false`.

## 2026-11-15 update: third independently dated historical vintage and run-failure diagnostics

A **third original EIA-930 ZIP historical snapshot** was verified through public Zenodo record [15568995](https://zenodo.org/records/15568995) dated 2025-06-05: `eia930-2023half1.zip` MD5 `691d52a09eff623571a4f18d504c0d25`. It precedes the 2025-11-23 archive (record 17688027, MD5 `122e5d253321b7baef657a4880f9a579`) and the 2026-09 record (22215263, MD5 `1b4acef4e1ec596cf92e7658f9be64c7`).

The original source-comparison program and the GitHub Actions workflow have been expanded to **download all three raw archives** with their original pinned MD5 values and explicitly compare the same 11 SRP UTC interval-start hours across three chronological snapshots. In addition to zip and uncompressed Balance CSV SHA-256 values, it emits:

- June → November changed-hour count;
- November → September changed-hour count;
- June → September changed-hour count;
- any hours that changed in November but reverted to June's value in September;
- missing-hour and archive-hash failure QA (fail-closed, uploaded as an Actions artifact).

Synthetic regression tests were added for **three-vintage differences, a missing hour in the earliest snapshot, and an intermediate revision subsequently reversed**. No training/validation source observation is altered by comparison. The actual 2023 source ZIP contents have not been obtained in this chat from the remote workflow, so **none of these three source-hour change counts is claimed as a verified empirical result**. Existing GitHub connector methods return no completed downstream run ID; this does not establish whether the push-triggered workflow ran.

The archived ZIP MD5 values differ: this is evidence that *archives are not byte-identical*, **not** evidence that SRP demand was corrected. Formal source-error confirmation and spatial-demand geography admission remain outstanding, and `model_training_permitted=false`. C-1 frozen.
