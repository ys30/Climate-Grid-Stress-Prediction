# C-2 E1 — Source-authenticated CEC 1306A detail grain and GWh conservation (2026-11-24)

## What was implemented in this turn

Added `scripts/c2_cec_1306a_source_detail_aggregation.py`, `tests/test_c2_cec_1306a_source_detail_aggregation.py` (seven synthetic-only contract tests) and updated the existing `c2-cec-joint-geo-contracts.yml` GitHub workflow to execute these tests on changes.

**This is a proposed normalization and source-integrity contract, NOT a claim to have downloaded original CEC 1306A county×UDC customer-level filings.**

The previously implemented joint-source gate rightly rejects duplicate *normalized* county×UDC×sector×month cells. But raw filings can be broken out by customer class, rate tariff and NAICS, which must first be aggregated at an **explicit, audited grain**. This source-only preprocessor requires:

- A byte-authenticated original-to-normalized detail CSV with fields `source_row_id,year,month,cec_county_number,udc_id,sector,customer_class,rate_class,naics,gwh`. This is a researcher-defined normalized schema and not an assertion about native CEC workbook headings.
- Explicit unique nonblank original `source_row_id` (prevents duplicate raw filing records), mandatory nonblank stratification dimensions (prevents accidental mixing), valid year/month, source SHA-256 and documented original release.
- A distinct byte-pinned, independently **reviewed** CEC county-number-to-California-FIPS mapping. Special/unmapped county codes, including `00/99`, are not assigned to a physical county.
- Positive or zero finite GWh values, no missing-to-zero imputation.
- A documented and approved raw→normalized schema lineage flag `normalized_detail_schema_reviewed=true` in the source manifest. The flag is **self-declared by the caller** and is not an independently certified evidence source.
- Summation of separate eligible customer, rate and NAICS detail to **unique month×county×UDC×sector** candidate GWh, with total original-to-normalized energy conservation, source SHA records, and no model admission.
- All results remain `historical_operational_BA_geography_approved=false`, `hourly_load_geography_approved=false`, `model_training_permitted=false`. It does not calculate geographic BA weights.

Example source-only execution after an authentic, lawful and independently reviewed release has been acquired:

```bash
python scripts/c2_cec_1306a_source_detail_aggregation.py \
  --detail inputs/1306a_verified_normalized_detail.csv \
  --county-map inputs/cec_county_map.csv \
  --manifest inputs/provenance.json \
  --out evidence/cec_1306a_monthly_aggregate
python -m unittest discover -s tests -p 'test_c2_cec_1306a_source_detail_aggregation.py' -v
```

Then pass `CEC_1306A_CANDIDATE_MONTHLY_COUNTY_UDC_SECTOR.csv` to the **existing independent** CEC 1305/1306A member-identity inspector, with a fresh SHA-pinned manifest and original-to-derived lineage. A successful join would still represent *conditional candidate* monthly association, not historical BA operating boundaries or observed hourly customer loads.

## Verification status

Files were committed to the repository and the workflow updated to run both the county-ID/member-source and detail-aggregation tests, but **this turn did not independently verify GitHub Actions execution or successful passing of the new exact repository tests**. Seven committed tests are synthetic fixtures, not observational results.

## Scientifically necessary caveats

Original 1306A filing dimensions may include multiple reporting fields/submissions, accounting conventions, unknown/suppressed counties and distinct supply/delivery measures. Before use, a research reviewer must verify source column definitions, reporting units, duplicate/amendment rules, and what sector/classification granularity is actually additive. An apparently unique row ID or declared source kind is not itself evidence that data are the original CEC release.

The 2020–25 six-year EIA-930/ERA5 source panel is real but uses historically unapproved 2018 BA masks; 2025 was explored and is not an untouched prospective holdout; AZPS 2023 annual EIA canonical QA remains failed. The source-vintage discrepancies remain unresolved. No model training, causal attribution, SSP projections or PyPSA adequacy claims are made. **C-1 remains frozen.**
