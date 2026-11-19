# E2 Wave 1: validated real EIA demand cohorts — evidence checkpoint

Date: 2026-11-18/19 UTC. This record is sourced from a complete first-wave
GitHub Actions run [44433236896](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44433236896),
plus the independently downloaded GitHub Actions ZIP artifacts. It does not
include ERA5, model training or climate attribution.

## Verified EIA-year datasets

| BA-year | Valid hours | Coverage | Mean demand MW | Minimum MW | Maximum MW | Hourly sum MWh |
|---|---:|---:|---:|---:|---:|---:|
| CISO 2024 (separate pilot run) | 8784 | 100% | 25504.36 | 14794 | 47571 | 224030258 |
| AZPS 2024 | 8784 | 100% | 4098.36 | 1975 | 11308 | 35999972 |
| BPAT 2024 | 8784 | 100% | 6724.26 | 4712 | 11496 | 59065880 |
| CISO 2025 | 8760 | 100% | 25573.49 | 11819 | 43860 | 224023764 |

The three Wave 1 ZIP artifacts were independently reopened. Every derived
CSV SHA-256 matches its source manifest, annual source QA says `pass: true`,
and each listed observation is a finite nonnegative original reported EIA
demand. The previously verified CISO 2024 result is from separate run
[44427373589](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44427373589).

### SHA-256 of original UTC-start demand CSVs

- AZPS 2024: `cc8d98afb7e6b955e89184f357343fe0ef7563460bfeb039f3675af7ffb2a954`
- BPAT 2024: `0ad50a220163671d93c825082cdbd320a752b35db8e65c993fb1a002b6daedb2`
- CISO 2025: `85ad6b398f9beffe29235d947f431b3c27ceea0ae9a16ac531fd382d1201e7ec`
- CISO 2024: `375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c`

## Why the five other Wave 1 cohorts originally failed

The original pipeline treated EIA's published null demand observations as
fatal during source download. Real logs show first failures in the downloader:

- CISO 2020 HE 2020-02-14T04
- CISO 2021 HE 2021-08-29T06
- CISO 2022 HE 2022-01-05T10
- CISO 2023 HE 2023-10-31T21
- SRP 2024 HE 2024-03-12T08

These are **first error timestamps**, not annual missing-hour totals. Source
data were not replaced with zero or interpolated. The revised downloader
preserves blanks, clock converter preserves the missing-value marker, annual
audit distinguishes source timestamp coverage from valid demand coverage and
applies the predeclared 98% threshold. Invalid nonblank values still block
eligibility; the weather join excludes explicitly missing demand from
paired hours.

The corrected workflow was committed at
`0b5045351ef5541543d6c18add6ba49eafe53b00` and is configured to
launch a fresh Wave 1 on push. **Do not count the five previously failed
cohorts as complete until the new run's source manifests and annual gates
have been checked.**

## Scope guards

- **4/24 distinct BA-years** are independently validated as of this
  checkpoint; same-BA successive reruns do not increase the count.
- No county retail-sales electricity allocation is inferred from EIA demand.
- No regional weather association, ERA5 spatial proxy, forecast skill,
  climate-change attribution, or future SSP/PyPSA stress conclusion follows
  from these observational summaries.
- C-1's frozen results are unchanged.
