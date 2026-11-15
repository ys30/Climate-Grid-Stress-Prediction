# C-2 E1 → E2 admission decision and next execution protocol
Date (Mountain): 2026-11-14
Status: SOURCE PROVENANCE CLEARED; EMPIRICAL MODEL ADMISSION BLOCKED.

## Verified record (not inferred results)
- Reference commit: 94da086f7b25439ed0516e539f5c9c8df23c292d.
- Version-aware original PUDL v2026.10.0 provenance check: SUCCESS, run 43670320754, artifact 14144762435, SHA256 428f82144297baa1c4041fb0185207aa171ec336bf1e271f7c88f82e2ba5267f.
- E1 audit explicitly reports 2,688 actual ERA5 A/B/C observations and 1,110 annual BA-county memberships checked for source identity. These are NOT a complete BA-hour demand/weather training panel.
- Corrected state-scoped BA → utility → county join run 43672928429 was still QUEUED at last written observation. No success, counts, intersection, Jaccard or accuracy may be inferred from the queued record.
- GEO_HISTORICAL_BA_FOOTPRINT, GEO_LOAD_RELEVANCE and LOAD_QUALITY_HOLDOUT_PROTOCOL remain OPEN/BLOCKED.
- model_training_permitted=false; do not describe E2 estimates as obtained.

## Execution order: deterministic and falsifiable
1. Verify completed status and artifact existence for workflow e1-PUDL-utility-state-county and the independent e1-PUDL-utility-vs-BA-county-source-audit workflow. Record workflow run ID, commit SHA, SHA256 of each downloaded archive, row counts and schema. A queued/cancelled/failing run does NOT count as a verified result.
2. For each of 4 BAs × 6 years, perform county FIPS exact-set comparison of state-limited utility association vs frozen original PUDL BA-county set, report |A|, |B|, |A ∩ B|, |A \\ B|, |B \\ A|, Jaccard, duplicates, missing utility-state combinations, BA-assignment multiplicity, and cross-state inflation in the unrestricted union. Reject null/invalid FIPS rather than silently coercing them.
3. Interpret this comparison ONLY as disagreement between two administrative source geographies. Neither service territory union nor annual BA-county union represents verified electric load allocation. Do not select weights by maximizing held-out prediction metrics before a preregistered evaluation.
4. Construct an independently auditable EIA-930 demand panel, BA-by-hour, 2020–2025: explicit hour-ending → interval-start UTC conversion, original timestamps and source/retrieval vintage, 1-hour uniqueness, duplicates/conflicts, missingness, valid demand definition and anomaly flags. Do not impute missing demand into gate statistics.
5. Match independently sourced ERA5 hourly spatial fields, with original source hashes and a documented, ex-ante spatial assignment. Evaluate at least three exposure alternatives where identified: simple geographic equal-area, population-weighted, and observed load weights ONLY where customer/load provenance exists. The current A/B/C observed weather rows do not alone establish BA-wide exposure.
6. Freeze full complete-case BA-hour coverage tables by BA/year/season and window, UTC clock tests, and minimum 3 complete annual cycles. Train period 2020–2022, tune 2023 and test 2024–2025 are candidates, NOT automatically authorized. Assess EIA revisions and COVID/structural breaks.
7. Record release decision in a machine-readable gate manifest: `PROVENANCE_PUDL_RELEASE`, `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE`, `LOAD_QUALITY_HOLDOUT_PROTOCOL`; `model_training_permitted` = true ONLY when all required gates independently pass.

## Prospective E2 analysis (blocked until admission)
- Compare calendar/seasonal naive, segmented degree-day or GAM, and boosted trees using rolling-origin and untouched chronological holdout; pre-register target metric, training-only transformations, extreme-heat bins and BA-stratified metrics.
- Primary observational target: EIA-930 reported hourly BA demand. Do not describe feature importance as causal attribution.
- Weather-normalization uses the empirical model with fixed calendar/infrastructure controls, observed-vs-resampled reference weather, and multi-day/year block bootstrap. Anthropogenic climate attribution separately requires a defensible ALL-vs-NAT climate counterfactual; otherwise label not identified.
- Do not propagate unvalidated models or synthetic weather into E3/E4 as calibrated forecast or blackout probability.

## Future climate safeguard
- Primary five paths: SSP1-1.9, SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5. NASA NEX-GDDP-CMIP6 supplies four Tier-1 pathways (126/245/370/585), daily resolution, not 119. SSP1-1.9 requires documented comparable extra source/processing and common GCM intersection.
- Preserve up-to-30 climate × GCM × portfolio families and maximum 24 core PyPSA optimizations; do not multiply experiments because some data become available.
- C-1 remains frozen and is not modified by this decision log.

## Before any manuscript Results claim
Attach actual source artifact, run link, SHA256, parameter settings, held-out test metrics and uncertainty. CI passing a software-contract test is not evidence of model skill or statistical identification.
