# C-2 — CEC 1306A disjoint-measure admission amendment (2026-11-24)

## Observed software defect and committed correction

The source-only CEC normalized-detail preprocessor previously asserted `conservation_verified=true` if output county×UDC×sector×month GWh matched the sum of all input records. **This necessary arithmetic test does not rule out source double counting** if the inputs contain both a subtotal and its constituent categories, multiple measurement bases, or an original filing alongside an amendment.

The code now refuses to aggregate *unless a researcher has explicitly supplied all of these separate source-level reviews* in the SHA-pinned manifest:

- `energy_measure: "delivered_electricity_gwh"`: the input is not a mix of generation, retail billed energy, electricity delivered or other measures
- `detail_cells_confirmed_disjoint: true`: the original aggregation grain excludes overlapping totals and subtotals
- `filing_amendments_resolved: true`: amended/corrected filings have superseded duplicate old submissions
- `denominator_and_sector_scope_reviewed: true`: original sector definitions, calendar and accounting scope are consistently additive

The preexisting flag `normalized_detail_schema_reviewed: true` and SHA-pinned original-to-normalized inputs remain required. The new output explicitly describes these as **declared review status**, not independent authentication.

### Test coverage

Four new synthetic contract tests reject each invalid state separately; the file now contains **11 source-only test methods**, alongside **14** CEC member/geographic crosswalk tests, both selected by `.github/workflows/c2-cec-joint-geo-contracts.yml`. No new real CEC 1305 or 1306A datasets were accessed. GitHub commit associated workflow runs were inspected through the available connector, which reports pull-request-triggered runs only; no matching runs were returned. That is **not a successful or failed CI result**, and CI pass must not be assumed.

### Scientifically material implications

Source GWh conservation alone cannot prove that a reported “consumption” field is a mutually exclusive measure of BA load. Even after the four declarations, a caller can falsely assert them; **a separately reviewed source file, release/version, corrected-filing disposition, and original line-item lineage** must support every flag before descriptive reuse. Utility association and month-level GWh are not the operating BA polygon or observed geolocated hourly demand.

CEC county special codes must not be mapped to physical FIPS without source justification; regional CA-only source coverage does not establish whole-AZPS, BPAT or SRP operating geography. No formal geography gate, canonical EIA vintage, 2025 untouched holdout, causal attribution, CMIP6 SSP projection or PyPSA adequacy model has been approved. **C-1 unchanged**.

### Source request priority

Retrieve publicly releasable dated CEC 1305 control-area UDC membership and CEC 1306A joint county×UDC breakdown with revision metadata and field-level accounting definitions. Independently check which records are increments versus totals or corrected filings. Only *then* evaluate the source-only code against observed originals.
