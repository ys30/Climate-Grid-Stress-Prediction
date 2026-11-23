# C-2 BA-0: authentic four-month EIA-930 × ERA5 UTC source match — 2026-11-22

## Actual execution, not a CI-fixture simulation

On 2026-11-22, original completed GitHub Actions artifacts were downloaded and validated locally:

- Four real public ARCO ERA5 January/July 2023/2025 source archives, Actions run [43659672871](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43659672871), each 2,976 four-BA×hour rows. Individual hourly CSV digests match original embedded source manifests.
- Seven canonical EIA-930 BA-year archives from source-verified Wave 1/3 runs: CISO/BPAT/SRP for 2023; CISO/AZPS/BPAT/SRP for 2025. Each UTC-start CSV SHA256 matches its source manifest; source hour-ending -> UTC-start labels were independently checked.
- Total authenticated ERA5 area-proxy rows: **11,904** per candidate A/B dataset.
- Total exact EIA demand × ERA5 paired rows: **10,416** = 14 BA×months × 744 unique UTC hours.
- Twelve? No: **14 of 16 BA×months** were joined at exactly 744/744 hours. AZPS Jan/Jul 2023 were excluded due to their annual **canonical source gate failure**, not ERA5 incompleteness.
- A/B proxies are *HIFLD 2018 candidate* and *2024 TIGER county candidate*, **not** certified operational BA footprint or load-weighted exposure.
- No model fitting, 2025 held-out evaluation, BA geographic certification, causal climate attribution, or SSP/PyPSA forecasting was performed.

## Source-clock paired diagnostic

| BA | 2023 Jan | 2023 Jul | 2025 Jan | 2025 Jul |
|---|---:|---:|---:|---:|
| CISO | 744 | 744 | 744 | 744 |
| AZPS | blocked, strict annual source failure | blocked, strict annual source failure | 744 | 744 |
| BPAT | 744 | 744 | 744 | 744 |
| SRP | 744 | 744 | 744 | 744 |

**Observed area-proxy sensitivity:** HIFLD vs TIGER mean temperature differences (TIGER minus HIFLD) were generally nonzero. For example, SRP 2023-01 = -1.867°C, AZPS 2025-01 = -2.060°C, CISO 2025-07 = -0.170°C. These are source-dependent mask differences, not climate forcing or BA demand-temperature estimates.

## Output and archival audit

Local user delivery: `C2_BA0_Real_EIA930_ERA5_4Month_Source_Audit_2026-11-22.zip`, 1,295,571 bytes, SHA-256:

`4e199fe7f0b36c90583f164a10656b3c7f4399b2bd3c3fe9f324f7b40db4c6c7`

It contains 11 original artifact archives, four derived CSVs, local source-join script, an explanatory README, per-source SHA provenance JSON, and a package SHA inventory. The ZIP contents were reopened and all 18 indexed file digests checked. **The download package was delivered separately to the researcher; the original real-data bytes are not committed to this public GitHub repository.**

## Required next gates

1. Promote only after independent CISO/AZPS/BPAT/SRP year-appropriate actual operational BA footprint and area weighting assessment. Both weather masks remain unapproved.
2. Establish full annual 2020–2025 ERA5 hourly variables (not four isolated months), source version checks and complete case gate.
3. Keep 2024/2025 held-out values sealed for model-choice purposes. These files were joined for source interoperability only.
4. Resolve AZPS 2023 canonical negative readings with published source correction or keep excluded and report separate noncanonical sensitivity.
5. Do not conflate source-clock integration with climatic attribution, predictive generalization, or PyPSA grid adequacy.

C-1 remains frozen.
