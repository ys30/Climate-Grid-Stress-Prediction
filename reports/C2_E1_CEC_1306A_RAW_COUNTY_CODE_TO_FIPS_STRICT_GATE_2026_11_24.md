# C-2 E1: correct CEC 1306A raw county numbering before any geographic admission (2026-11-24)

## Official source discovery (2025 reporting format)

The California Energy Commission's [July 2025 CEC-1306A Schedule 1 instructions](https://www.energy.ca.gov/sites/default/files/2025-07/1306A_Instructions_07142025_ada.pdf) show that original raw filers provide **CEC County Number** (ordinary county codes 1–58, plus 00 and 99 reserved/unknown classifications), **Company Number**, **Year**, **Month Number**, **Customer Type**, **Rate Class**, **NAICS Code**, **Number of Customers**, **Sales/Delivery Amount (kWh)** and **Revenue**. The raw form **does not itself provide a five-character federal County FIPS**. Consequently, a normalization that treats CEC County Number as FIPS is scientifically wrong, and aggregating raw rows with distinct customer/rate/NAICS classes without an auditable grain contract may double count or discard valid filings.

CEC [control-area reporting forms](https://www.energy.ca.gov/resources/forms/forms-instructions-reporting-electric-and-natural-gas-sales-and-electric) state that 1305 submissions list member UDCs and join/leave changes; membership cannot be assumed constant through a month if actual changes occurred.

## Implemented, fail-closed correction

The existing `scripts/c2_cec_joint_geo_source_gate.py` now expects **four separately SHA-pinned source/normalization inputs**:

1. `membership_1305`: `year,month,ba,udc_id,membership_effective_whole_month` (latter is a *reviewed derived indicator*, not an asserted original 1305 field);
2. `county_consumption_1306A`: `year,month,cec_county_number,county_fips,udc_id,sector,gwh` (**post-normalization/aggregation**; cannot directly consume original raw Schedule 1);
3. `udc_eia_crosswalk`: `udc_id,eia_utility_id,reviewed` (reviewed identity bridge);
4. `cec_county_crosswalk`: `cec_county_number,county_fips,reviewed` (independently reviewed code translation).

The source manifest must contain corresponding four `files` entries, each with exact `sha256` and `source_release`. First two should declare `source_kind:official_original`, but such a self-declaration does **not** independently authenticate origin; raw releases and field mapping must be retained externally.

For each consumption row, the inspector now requires a matching, reviewed **CEC County Number 1–58 → California FIPS 06xxx** mapping and rejects unmapped, foreign-state, special `00/99`, duplicate/nonunique code mappings. It also retains the previous whole-month membership blocker, duplicate normalized county×UDC×sector×month blocker, unreviewed UDC-ID identity blocker and strict missing ≠ 0 policy.

**The four-source checker is for California-reported consumption only.** It does not validate other states' AZPS/BPAT/SRP service areas or the operation-year BA footprint of CISO, and it must never infer complete cross-state BA coverage.

## Execution evidence and status

- Original GitHub source and test files were **updated**. The official repo's test module now contains **14** tests (four added county mapping tests).
- A locally reconstructed equivalent implementation (not byte-identical to GitHub's source) and **15 corresponding local tests** were executed with Python: **15/15 passed after fixing test fixture input order**. This supports the logic but **does not constitute confirmed successful GitHub Actions execution**.
- Source inspection still has **no actual authenticated joint historical CEC 1305/1306A rows**. The public CEC consumption summary sheets have separate county and UDC marginals; no actual public joint record was added. No energy allocation or model training conducted.

To run, provide an authenticated, separately reviewable original-data normalization and call:

```bash
python scripts/c2_cec_joint_geo_source_gate.py \
  --membership normalized_1305.csv \
  --consumption normalized_1306A.csv \
  --crosswalk reviewed_udc_eia.csv \
  --county-map reviewed_cec_county_to_fips.csv \
  --manifest original_source_manifest.json \
  --output evidence/cec_geo_source_only_audit.json
```

The normalized sector-level grain must be independently verified against the actual raw Customer Type, Rate Class and NAICS codes; a duplicate normalized row is not automatically a duplicate raw filing. Original kWh must be converted to GWh only with source-proven conversion; `00/99` special county energy must remain explicitly unallocated, not zeroed or assigned to an invented county.

**Scientific status unchanged:** historical BA footprint and load-geographic weather exposure BLOCKED; EIA demand-vintage QA and 2025 exploratory holdout caveats persist; no model/CMIP6/PyPSA results authorized; C-1 frozen.
