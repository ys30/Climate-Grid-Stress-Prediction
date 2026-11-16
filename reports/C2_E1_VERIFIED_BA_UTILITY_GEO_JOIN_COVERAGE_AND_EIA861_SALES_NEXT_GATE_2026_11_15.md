# C2 E1 — independently verified PUDL v2026.10 utility–BA–state geographic source coverage (2026-11-15)

**Real archived 2020–2025 EIA861 source crosswalk audit; NOT observed electricity-demand geography.** C-1 frozen and E2 model admission blocked.

## Original source and reproducibility

PUDL v2026.10 utility–BA–state original audit, successful GitHub Actions artifact `14144934238`, archive SHA256 `0e3d5ac5556b155456deb79bbb78be4b707907043764faca29edf1552721385e`, member `EIA861_2020_25_fourBA_utility_state_counts_SOURCE_ONLY.csv` SHA256 `e70ac12859b47e24d07cff76201e85a33d3f6c4701e040ed0ea453e00f3e03dc`. Independently re-read and validated 24 unique BA/year entries, original source count identities, and all formal training approval flags false. Per-BA/year CSV, period summary, JSON SHA audit, reproduction script packaged as `C2_E1_BA_UTILITY_GEOGRAPHIC_COVERAGE_20261115.zip`.

## Actual 2020–2023 training + validation source associations

| BA | Source utility–state association records | County-source matched | Matched association share | Excluded cross-state county-association slots |
|---|---:|---:|---:|---:|
| AZPS | 96 | 48 | 50.00% | 0 |
| BPAT | 443 | 436 | 98.42% | 716 |
| CISO | 361 | 154 | 42.66% | 19 |
| SRP | 33 | 8 | 24.24% | 0 |

## Actual 2020–2025 source-geographic provenance

| BA | Source association records | County-source matched | Matched share | Excluded cross-state county-association slots |
|---|---:|---:|---:|---:|
| AZPS | 146 | 72 | 49.32% | 0 |
| BPAT | 670 | 659 | 98.36% | 1,096 |
| CISO | 550 | 236 | 42.91% | 31 |
| SRP | 52 | 12 | 23.08% | 0 |
| **Total** | **1,418** | **979** | **69.04%** | **1,127** |

All counted entities are **source association records**, not exclusive customers, retail MWh, BA hourly demand, unique utility boundaries, or validated county load distributions. The excluded county-association *slots* are a different count unit and must not be added to source association totals. BPAT's very high join rate coexists with substantial excluded cross-state county slots: this precludes any claim that simple match rates validate a BA's historical load geography. AZPS, CISO and SRP have especially low coverage of source association rows.

## Confirmed route to load-related geographic verification

EIA Form 861 publishes annual **customer counts and sales MWh** by utility, state, balancing authority and service class: https://www.eia.gov/electricity/data/eia861/ . PUDL's independently defined `core_eia861__yearly_sales` provides `utility_id_eia`, `state`, `report_date`, `balancing_authority_code_eia`, `customer_class`, `service_type`, `business_model`, `sales_mwh`, `customers`, `data_observed` and `data_maturity`: https://data.catalyst.coop/preview/pudl/core_eia861__yearly_sales .

Next meaningful test: join a **tagged, immutable PUDL sales release** onto the existing original BA–utility–state associations using year, BA code, utility ID and state; report separately the observed MWh and customers in county-matched versus unmatched association classes, by service_type and business_model, disallowing class-total plus component-class double counting and `data_observed=false` leakage. This measures the business relevance of county-source coverage; it still does **not** identify actual load by county, subcounty grid cell or hour. **No sales MWh source was downloaded or used in the present results**, and no sales-weighted exposure has been estimated.

Scientific admission remains `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `GEO_LOAD_RELEVANCE=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`, `model_training_permitted=false`. The 2024–2025 demand test is not used for modeling or validation; C-1 remains frozen.
