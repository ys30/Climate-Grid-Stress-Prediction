# C2 E1 winter–summer 48-hour real ARCO ERA5 × EIA-930 source pairing

Updated: 2026-11-13 (Mountain Time).

## Experimental design
This is an E1 reproducibility check, NOT climate attribution, an approved historical weather–demand modeling panel, or a trained prediction:
- Winter: 2023-01-15T00:00:00Z to 2023-01-16T23:00:00Z.
- Summer: 2023-07-01T00:00:00Z to 2023-07-02T23:00:00Z.
- Four BAs: AZPS, BPAT, CISO, SRP. Exactly 48 UTC hours per BA and season; 192 potential source pairs per season, 384 total.
- ERA5 2m temperature: public ARCO hourly 0.25° gridded reanalysis, source grid 5,472 cells/hour in the required Western U.S. bounding rectangle. All intersected grid cells included in the four BA-weighted average (AZPS=265, BPAT=1,557, CISO=662, SRP=55). Source weight table frozen from CI 43548907152; SHA256 `e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3`.
- EIA-930 official reported raw demand reconciled to UTC *interval-start* hours from 2022 H2 plus 2023 H1/H2 source documents; original files not modified. Exact key alignment, no source imputation or weather interpolation.
- All weather exposures use *unapproved candidate geographic boundaries* from HIFLD national control area source YEAR=2018, with Shapely `make_valid` candidate fixes. CISO has ~7.08% topology-area sensitivity; AZPS/SRP candidate geographic intersection ~96.66% of SRP candidate area. No training authorized.

## Actually observed in the first computation run
Original CI run 43554852808 successfully computed the two independent winter and summer outputs, but overall GitHub workflow failed at the artifact-upload step because the artifact name included an illegal colon (`:`) from an ISO 8601 time. This is a packaging failure, not a numerical calculation failure.

Winter diagnostics (2023 Jan 15–16; 192 exact BA-hours):
| BA | EIA raw demand range MW | Derived experimental ERA5 area temperature range °C |
|---|---|---|
| AZPS | 2,778–3,680 | 6.509511–14.176077 |
| BPAT | 5,665–7,732 | −1.761566–4.437173 |
| CISO | 19,899–26,613 | 5.307045–8.927517 |
| SRP | 2,606–3,594 | 9.838004–17.294365 |

Summer diagnostics (2023 Jul 1–2; 192 exact BA-hours):
| BA | EIA raw demand range MW | Derived experimental ERA5 area temperature range °C |
|---|---|---|
| AZPS | 3,438–7,004 | 21.068864–39.453480 |
| BPAT | 4,965–7,785 | 12.729409–28.503909 |
| CISO | 22,537–35,936 | 20.475391–35.691343 |
| SRP | 3,177–7,159 | 25.425508–42.853046 |

Both 48-hour windows had exactly 192 source-paired rows and **zero EIA original-demand candidate anomalies under the existing flag rule**. Zero flags in these windows does not imply the wider EIA source is anomaly-free. All data remain *diagnostic only* and training is blocked.

## Workflow packaging fix
Run https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43554916894 re-executes the same two independent matrix computations but uses artifact names `c2-e1-real-two-day-source-audit-winter` and `c2-e1-real-two-day-source-audit-summer`, avoiding invalid colon characters. Do **not** state this corrected run passed until its complete jobs and artifact uploads are verified.

Code: `src/c2_era5_seasonal_source_audit.py`. Workflow: `.github/workflows/e1-seasonal-real-source-audit.yml`.

## Next E1 / E2 gate
1. Verify the corrected artifact uploads and inspect the emitted paired source CSVs and manifests.
2. Extend measured source coverage to additional seasonal/yearly windows without assuming 2023 alone validates 2020–2025 weather availability.
3. Compare geographically robust alternates or independent BA service-area source vintages; obtain a documented scientific decision on 2018 polygon applicability and AZPS/SRP geographic overlap. Explicit audit approvals remain mandatory for `c2_weather_join.py`.
4. Only following geometry and source QA approval build immutable 2020–2025 datasets and calibrate calendar/GAM/XGBoost with 2020–2022 train, 2023 validation and 2024–2025 sealed test. Reserve ALL/NAT forcing for any anthropogenic climate attribution.

## Final verified result: BOTH SEASONS CI SUCCESS and artifacts retained

Corrected rerun https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43554916894 **COMPLETED SUCCESS** for BOTH winter and summer jobs. In addition to reproducing the 192 row per season measurements, the workflow uploaded both paired-source CSV/artifact bundles:

- Winter artifact ID `14097603611`: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43554916894/artifacts/14097603611 ; SHA256 compressed artifact `22ff4eb5141980c90e1645c2058b802cc1a72ec1349175a5c2c65dbb29cc4294`.
- Summer artifact ID `14097746782`: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43554916894/artifacts/14097746782 ; SHA256 compressed artifact `5300c2e9f714f0837a03b522da0eeb1360e131498242f8c00c37edd53eec9452`.

Both real-source windows had 192 exact UTC paired records each and 0 flagged EIA-930 source anomalies in the selected two-day periods. Input weather weights remain unapproved candidate geography and all row-level training/validation eligibility flags remain false. No anthropogenic attribution or forecast skill is estimated.
