# C-2 decision memo: decouple BA-level historical demand evaluation from ZIP/county geolocation (2026-11-22)

## Evidence frozen at this decision point

- Source repo: `ys30/Climate-Grid-Stress-Prediction`; latest checked commit `6893086c2e5e2ac6116d7af17c2e3cf9522906f9`.
- Authenticated SCE 2020–2023 original 16-quarter cell-level audit: 143,778 source rows; 77,149 `Combined=Y`; 66,629 `Combined=N`; 93,349 blank kWh; 50,413 positive; 16 negative; zero literal kWh zeros; 105 additional ZIP×month×class records. Evidence: `reports/C2_E1_REAL_SCE_16Q_KWH_PRIVACY_SOURCE_ROWS_VERIFIED_2026_11_22.md`, CI 45043437708.
- SDG&E has its own 50 negative residential reported rows; never pool with SCE 16 without a documented harmonized definition.
- EIA-861 utility–county associations are not a unique spatial apportionment of sales; 2020–2023 reported electricity sales can be checked at source level but not allocated to counties by naive repetition or uniform shares.
- PG&E ZIP records not verified; historical CISO operational BA footprint not established.
- C-1 remains frozen at `6b549a6612f280646389f87bfc35453dd0e5d7dc`.

## Two independent scientific gates

### Gate BA-0 — temporal BA-level weather–demand benchmark (may proceed only after its own verification)

**Primary observation**: EIA-930 reported BA hourly demand (CISO, AZPS, BPAT, SRP initial cohort), keeping historical BA reporting vintage and clock semantics. This does **not** require utility ZIP-to-county load allocations.

**Permissible first exposure**: predeclared, reproducible ERA5 gridded, BA-associated unweighted area or fixed-site weather summaries explicitly labelled **weather proxies**. These do not represent identified load-weighted population or grid service areas. If BA footprint is not verified, choose designated fixed weather stations/points with a clear geographic representativeness caveat and do not call the resulting contrast spatial BA exposure or causal climate attribution.

**Admissions (all required before model fitting)**:
1. EIA-930 source vintage, download metadata, hash, demand units and API pagination / comprehensive source inventory documented.
2. Hour-ending versus interval-start UTC mapping independently checked; no duplicated or missing timestamps silently filled; daylight-saving years audited.
3. ERA5 source/license, spatial proxy definition, raw hashes, hour mapping, missingness inventory documented without test-era fitting.
4. BA-year complete-case and coverage audit shows >= 3 adequate annual cycles and no unresolved incompatible BA definitions; predeclare minimum coverage and acceptable gaps by BA-year, rather than discovering cutoffs after test evaluation.
5. Chronological split sealed: candidate 2020–2022 train, 2023 tune, 2024–2025 test, modified only by a documented pre-fit coverage gate; no holdout demand values are inspected for model selection.
6. Benchmarks, predictors, train-only transforms and metric specification frozen before fitting; leakage checks passed.

**Permitted claims after this gate**: out-of-time BA-hour demand prediction and *associations with the explicitly defined weather proxy*. Do not claim accurate BA-wide weather exposure, load-weighted causal temperature response, grid outages or climate-change attribution.

### Gate GEO-1 — county/utility-weighted demand exposure (remain BLOCKED)

Unlock only with publisher-backed SCE/SDG&E/PG&E donor-to-recipient combined ZIP crosswalk or separately measured geographic allocations; a vintage-correct HUD/USPS ZIP–county crosswalk; a defensible historical BA footprint and utility membership; treatment of suppressed/blank/negative kWh; and independently reconciled utility/county/BA totals. Combined ZIP rows and duplicate keys must not be blindly deduplicated or assigned to displayed ZIP.

Only after GEO-1 unlocks may the project assert county- or load-weighted hourly BA weather exposures. A physically meaningful BA electric service footprint is a separate requirement, not inferred merely from county names.

### Gate FUT-1 — CMIP6 scenario projection (remain BLOCKED)

- Validate common GCM models, historical baseline, variable definitions, and daily temporal resolution across documented SSP1-1.9 / SSP1-2.6 / SSP2-4.5 / SSP3-7.0 / SSP5-8.5 products. NASA NEX-GDDP-CMIP6 4-pathway coverage alone is not 5-pathway coverage.
- Evaluate holdout predictive skill and stable physical covariate transfer before future projections.
- Do not synthesize unvalidated hourly wind/radiation or imply hourly tail forecasting from daily climate projections.
- Keep PyPSA outputs assumption-conditioned stress *screens*, not outage probabilities.

## Execution order and stop decisions

1. Maintain the verified source-cell audit as an immutable result; keep the source ZIP/county model blocked.
2. Implement BA-0 **data inventory only**, using EIA-930 hourly demand and a separately labelled ERA5 weather proxy; record source versions, exact BA/year availability, clock QA, missingness and geographic proxy definition.
3. Review the BA-0 inventory against predeclared coverage thresholds. If inadequate, issue a feasibility finding and stop model claims. If adequate, freeze split + benchmark specification and then fit 3 preregistered model families.
4. In parallel, pursue GEO-1 source authorization / public crosswalks as a distinct workstream; failure of GEO-1 does not in itself prevent BA-0 observational forecasting.
5. Keep anthropogenic attribution absent without a justified natural-forcing counterfactual; keep FUT-1 and PyPSA model-calibrated projection claims blocked until their own prerequisites pass.

**No model fitting, skill scores, county apportionment, causal attribution or future stress results are claimed by this memo.** C-1 is not modified.
