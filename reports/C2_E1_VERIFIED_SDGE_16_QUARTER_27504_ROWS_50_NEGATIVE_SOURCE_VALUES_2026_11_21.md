# C-2 E1 — independently verified 16 quarters of original SDG&E public electric ZIP data (2026-11-21)

**New original-source milestone: all 16 of 16 2020–2023 quarterly publisher CSV files and associated SDG&E SHA-512 sidecars verified.** GitHub Actions original live-source [run 44920136951](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44920136951) **SUCCESS**, data-audit metadata artifact **14713797086**.

I downloaded and independently inspected artifact member `C2_SDGE_REAL_2020_2023_16_QUARTER_PROVENANCE.json`, SHA256:
`2588e31c747e944ae1333884c0cf05caf3a5653391b04f9384013b659455804a`.

## Independently recomputed annual original-record counts

| Year | Original rows | Combined=Y | Literal reported zero kWh | Positive reported kWh |
|---|---:|---:|---:|---:|
| 2020 | 6,876 | 5,697 | 4,701 | 2,175 |
| 2021 | 6,876 | 5,871 | 5,083 | 1,793 |
| 2022 | 6,876 | 5,944 | 5,269 | 1,585 |
| 2023 | 6,876 | 5,994 | 5,341 | 1,507 |
| **Total** | **27,504** | **23,506** | **20,394** | **7,060** |

**The remaining 50 original reported kWh values are negative.** They are neither blank nor zero, and their source validity has not yet been assessed against SDG&E accounting rules, self-generation/net-metering treatment, or possible adjustment conventions.

Original negative-record distribution:
- **2022 Q2: 18**
- **2022 Q3: 4**
- **2023 Q1: 1**
- **2023 Q2: 27**
- All remaining 12 quarters: **0**.

No duplicate `ZIP × month × customer_class` original keys were found across the 16 separate quarterly source files. This does **not** prove that ZIP labels correspond to independent physical recipient areas; publisher specifically describes privacy groupings with neighboring ZIPs.

## Scientific and QA implications

1. SDG&E's public original data is now source-acquired for all four 2020–23 years. The earlier claim of only 2020 Q1 being obtained is superseded.
2. Original source SHA-512 matching proves downloaded bytes correspond to publisher sidecars, **not** that all source values represent independent metered county consumption.
3. The high `Combined=Y` source prevalence (23,506 / 27,504) means reported positive kWh and literal zero values need recipient/donor geographic interpretation before using them for load weighting.
4. **Do not clip the 50 negative values to zero or delete them** until the original utility reporting explanation is documented. The source-only follow-up should enumerate quarter × `Combined` × customer_class × negative kWh rows with row position, never publish customer personal records.
5. This quarterly series is retail utility public ZIP usage; it is **not** CISO EIA-930 BA hourly demand, and does not resolve 2020–23 BA membership or spatial allocation.
6. Separate SCE exact duplicate raw-row job was queued and later failed on original XLSX header newline normalization, now corrected in `4cd6c46db6a859c36c95a2b6bbe22721359bda7c`; new run must be observed, not assumed successful.
7. Separate SCE 2020–23 original 16-quarter official-download-link discovery workflow is queued; actual original 16 XLSX hashes remain unverified.

**No source overwrite, no artificial ZIP-to-county allocation, no E2 model fitting.**
`GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`,
`GEO_LOAD_RELEVANCE=BLOCKED`,
`LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`,
`model_training_permitted=false`; C-1 frozen.

Program: `scripts/c2_sdge_real_2020_2023_sixteen_quarter_source_audit.py`;
workflow `.github/workflows/c2-sdge-16-quarter-source.yml`.
