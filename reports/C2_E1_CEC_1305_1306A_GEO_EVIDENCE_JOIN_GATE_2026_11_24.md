# C-2 — Evidence-admission matrix for CEC 1305/1306A geography (2026-11-24)

## New executable artifact

- `scripts/c2_cec_joint_geo_source_gate.py`: source-only *normalized input* QA for separately obtained CEC control-area/UDC member evidence (1305) and county×UDC sales/delivery evidence (1306A), plus researcher-reviewed EIA utility-ID crosswalk. Requires pinned SHA256, source release identifiers, 2020–2025 year/month, 5-digit FIPS, valid nonnegative GWh, no duplicate membership, and conservatively labels multi-BA/unknown-UDC cases without fractional allocation.
- `tests/test_c2_cec_joint_geo_source_gate.py`: six synthetic-only contract tests (source tampering, missing ≠ zero, invalid county FIPS, duplicate membership, nonexclusive BA associations, unconditional training block). **Tests committed, not independently run in this turn**; no claim of passing CI.
- Output JSON always has `historical_BA_footprint_approved=false`, `load_weighted_exposure_approved=false`, `model_training_permitted=false`. Even a well-formed matched association is not a historical geographic operating boundary or measured hourly BA customer weights.

### Why source identity is not load geography

CEC explicitly documents 1305 control-area reporting of monthly peak, hourly load, UDC membership, adjacent interchange, and changes to control-area participation; official [1305B instructions](https://www.energy.ca.gov/sites/default/files/2020-07/1305B_Instructions_ada.pdf). CEC 1306A collects UDC consumption by reporting county (and related dimensions); official [QFER intake](https://www.energy.ca.gov/rules-and-regulations/energy-suppliers-reporting/quarterly-fuel-and-energy-reporting-qfer) and [forms](https://www.energy.ca.gov/resources/forms/forms-instructions-reporting-electric-and-natural-gas-sales-and-electric). But [public consumption data files](https://www.energy.ca.gov/files/energy-consumption-data-files) distribute **separate agency and county marginals**; the independently joined historical **county×UDC** filing source has **not** been acquired or approved. A normalization schema is **not proof that the actual public source has these fields**, nor that the crosswalk is correct.

The existing four-BA 2020–2023 PUDL fixed-release observed retail-sales audit totals **924,201,242 MWh**, of which **757,691,947 MWh** is on multi-county source support, **146,292,284 MWh** conditionally one-county and **20,217,011 MWh** without county-source support. These are annual retail estimates and cannot serve as independently observed BA hourly weights.

### Schema contract, only after licensed original files and source review

Normalize separately, preserving original raw source:

```
1305 membership: year,month,ba,udc_id
1306A county delivered consumption: year,month,county_fips,udc_id,sector,gwh
reviewed identifier bridge: udc_id,eia_utility_id,reviewed
```

Source provenance JSON keys: `research_only:true`, `training_permitted:false`, `files.membership_1305`, `files.county_consumption_1306A`, `files.udc_eia_crosswalk`; each source entry must have `sha256` and `source_release`; the first two require `source_kind:"official_original"`. Preserve a *verified release* and field-level original-to-normalized mapping outside of this script. The manifest's declarative source type is **not an independent authentication service**.

```bash
python -m unittest tests.test_c2_cec_joint_geo_source_gate -v
python scripts/c2_cec_joint_geo_source_gate.py \
  --membership originals/normalized_1305.csv \
  --consumption originals/normalized_1306A.csv \
  --crosswalk originals/normalized_reviewed_ids.csv \
  --manifest originals/source_manifest.json \
  --output evidence/cec_joint_identity_gate.json
```

**No real 1305/1306A joint records were processed for this turn.** No evidence that 1305 data are publicly available at the needed historical level, or that confidentiality permits 1306A joins, was established. This code is a *future-source validation gate* and is not a fitted model, a completed scientific result, or a BA boundary certification.

## Actionable original data request

Existing [CEC evidence-request memo](C2_E1_CEC_1305_CONTROL_AREA_AND_1306A_COUNTY_UTILITY_SOURCE_REQUEST_2026_11_21.md) identifies distinct original-record access paths. The user's independent action is required to send a request; no messages were sent. Ask QFERGEN@energy.ca.gov for publicly accessible historical 1305 month-by-month UDC membership and effective changes; ask QFERDemand@energy.ca.gov whether de-identified/nonconfidential 1306A *county×UDC×year×sector* joint tables can be released, specifying years, data dictionary, disclosure rules and license. Do **not** assume respondent-portal privileges.

**Gates still blocked:** true 2020–25 BA operational geography, load-relevant geolocated weights, canonical EIA-930 source vintage, and prospective validation. AZPS2023 source gate remains failed; previously described 2025 demand has already been inspected, not pristine holdout. No causal attribution or SSP/PyPSA outputs. C-1 remains frozen.
