# C-2 E1 — independent operator-source geography evidence register (2026-11-25)

## Executed source discovery and artifact

Seven authentic public **official-source metadata leads** across CISO, BPAT, AZPS and SRP were identified, transcribed into a deterministic 7-row source register, and marked with temporal applicability, reuse restrictions and scientific gates. The Python generator and **7 local contract tests passed**, and the delivered ZIP was reopened and CRC-checked.

**Local delivered package:** `C2_C2_Operator_Independent_Geography_Source_Register_2026_11_25.zip` SHA256 `80f658e65980ccea5fe9b8e206398d1428a1a74e6ee678087cbf4f980d355fba`. Includes `OFFICIAL_OPERATOR_SOURCE_REGISTER.csv`, four-BA evidence coverage CSV, SHA manifest, `build_audit.py`, `test_source_register.py`, README. This records **metadata** and documented availability, not downloaded original operator GIS or FERC-714 report bytes.

### Evidence by operator

| EIA BA | Original official leads | What is publicly documented | Cannot claim |
|---|---|---|---|
| CISO | [CEC California BA Areas dataset](https://publish.data.ca.gov/dataset/balancing-authority-areas), [CAISO illustrative BA presentation](https://www.serc.org/docs/default-source/committee/oc-system-operator-subcommittee/2025-system-operator-conference/2025-serc-soc-caiso.pdf) | Current state BA map dataset, presentation with approximate BAA illustration | 2020–25 annual operational polygon lineage, BA hourly spatial customer weights |
| BPAT | [BPA BAA services](https://www.bpa.gov/energy-and-services/transmission/ancillary-services/balancing-authority-area), [BPA 2020–25 FERC-714 annual report index](https://transmission.bpa.gov/business/operations/ferc714/default.aspx) | BPA operator services; separate report links for all **six 2020–25 years** covering annual BAA loads and interchanges | Matched operator values have **not yet been extracted**; no county/hour geolocation |
| AZPS | [DOE-hosted 2025-effective WECC area exhibit](https://www.energy.gov/documents/craig-order-202-26-31-pios-exhibits-2-131-2-170-july-24-2026) | Dated AZPS participating BAA context, not a full 2020–25 vintage series | Annual operating footprint certification |
| SRP | [SRP retail service geography](https://www.srpnet.com/about/service-area-territory), [SRP corporate GIS **metadata only**](https://services2.arcgis.com/ICaY8VX3lsUsMBRl/arcgis/rest/services/SRP_PSA/FeatureServer/3/metadata?f=html&format=default) | Corporate SRP power *service area* metadata describes 1950s contractual basis, excluded contract territories, explicit restricted rights | DO NOT distribute restricted GIS geometry; retail footprint != SRP BAA |

### Scientific decision

The existing EIA-861/PUDL support-union audit found unchanging county unions, but operator metadata confirms why this cannot certify true historical BAA operation or hourly climate exposure. All seven new leads remain exploratory sources; no original yearly operator geometries acquired, no independent load-weighted hourly geography, **no model training**, no causal attribution, no SSP/CMIP6/PyPSA stress claims. EIA-930 source-vintage discrepancies remain open. C-1 remains frozen.

**Highest-yield next actual analysis:** download and source-hash BPA's six original 2020–25 FERC-714 reports and independently compare the **well-defined annual BPAT BAA load** with EIA-930 demand where compatible; do not substitute retail sales, net generation or annual peak for annual demand totals. For CISO/Arizona BAs, seek dated operational BA membership or lawful GIS releases.