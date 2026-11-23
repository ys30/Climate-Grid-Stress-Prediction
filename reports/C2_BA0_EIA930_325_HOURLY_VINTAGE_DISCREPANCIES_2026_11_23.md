# C-2 BA-0: 325 real EIA-930 hourly source-vintage discrepancies (2026-11-23)

**Executed row-by-row** on the original archived 2020–2025 all-month real EIA-930×ERA5 source ZIP and **12 separately downloaded, SHA-verified annual official EIA-930 artifact ZIPs**, compared by exact `(BA, UTC interval start)`. The original annual raw **hour-ending** data and the transformed UTC-start CSV are both checked against their original manifests; conversion from HE to start is verified on each row. The old consolidated original inner gzip SHA256 is `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

The comparison covers AZPS 2021/2025; BPAT 2021/2023/2025; CISO 2021/2023/2024/2025; SRP 2021/2023/2025. Do not extrapolate row-level equality or mismatch results to the 12 other BA×years not included.

## Empirical result

**325 unique BA×UTC-hour discrepancies**:
- 174 values are numeric in both authentic artifacts, but differ;
- 99 source hours are blank in the old panel and numeric in the newer annual artifact;
- 51 old numerical demand hours are missing/null in the newer annual artifact;
- one hour is an absent key in the newer annual CISO 2021 extraction.

Key examples:
- **AZPS 2025:** **169 real numeric disagreements**, despite *identical* numeric-hour count. They cluster in April, July, August, September, and October; new minus old changes span −6,661 to +1,905 MW. The annual count-only comparison **missed this entirely**. Do not assert they are rounding-only or officially revised demand without evidence.
- **CISO 2024:** 48 previously blank demand hours, now numeric, clustered November 1–3 UTC.
- **CISO 2025:** another 48 old-blank/new-numeric hours around March 8–9 and November 1–2 UTC.
- **BPAT 2021:** 25 old-numeric/new-null hours concentrated Sep 15–16 UTC, plus one changed numeric value near Nov 7.
- **BPAT 2023:** 24 old-numeric/new-null hours Oct 24–25 UTC.
- **SRP 2025:** three old-blank/new-numeric and three changed-numeric hours.
- AZPS 2021, CISO 2021, SRP 2021 each have distinct single-hour discrepancies; some BA/year with identical counts have no mismatches.

This supersedes the prior simplistic interpretation that **8 BA-years with different numeric counts** exhaust the vintage problem. It also shows coherent 24/48-hour mismatch windows; these are **not proof of DST causality** because both sources were compared on common UTC keys. Original source artifacts are reproducibly hash-pinned, but they cannot alone establish whether EIA changed reported values or the older archive's ingestion and cleaning differed.

## Reproducible user delivery

`C2_C2_EIA930_12_Cohort_Hourly_Vintage_Reconciliation_2026_11_23.zip`, SHA256 `0851da12260daa65ddd598902545232db44d6c93bff44c8cb3ede49eb66c6bc6`, 3,512,473 bytes, contains 13 unchanged original source ZIPs; a standard-library-only exact-UTC and SHA verification script; 325-row changed-key CSV; 12-row annual audit; daily clusters; hash and source classifications; scientific limitations. This is **not** an official revised EIA dataset and is delivered to the user separately, not silently committed to the public repo.

**Scientific gate remains CLOSED:** No automated value overwrite/imputation, no ERA5 BA operating geography admission (old panel used unapproved 2018 HIFLD candidate land-area masks), no leakage-blind 2025 claim (previous exploration already occurred), and no model/causal/SSP/PyPSA claims. AZPS 2023 still fails canonical strict EIA source QA due to its original negative values.

**Next:** Diagnose 169 AZPS 2025 changes and recurrent CISO/BPAT contiguous day windows against original EIA source retrieval semantics; freeze a provenance-preserving precedence policy, then address dated actual BA operating areas and weather-load weighting. C-1 unchanged and frozen.
