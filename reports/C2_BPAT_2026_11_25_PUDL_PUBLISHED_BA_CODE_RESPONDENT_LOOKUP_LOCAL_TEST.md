# C-2 BPAT — public fixed-release annual BA-code respondent linkage preflight (2026-11-25)

## Major methodological correction

Previously C-2 attempted to discover the BPA FERC respondent using the name in `core_ferc714__respondent_id`, which contains a numeric `eia_code` that may identify either an EIA utility **or** an EIA balancing authority. A BPA name or nonempty numeric EIA code is therefore insufficient to prove linkage to the **BPAT** BA.

The official [PUDL v2026.10.0 dictionary](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html) documents the **published** `out_ferc714__summarized_demand` table with per-year `respondent_id_ferc714`, `respondent_name_ferc714`, `eia_code`, `respondent_type`, `balancing_authority_id_eia`, `balancing_authority_code_eia` and BA/utility names and IDs. The similarly named `_out_ferc714__categorized_respondents` is an **internal** processing table rather than the intended public query endpoint. The public annual summarized table includes derived demand metrics, so C-2 queries **identity metadata columns only** and does **not** use its demand annual MWh in cross-source validation.

## Actually committed

- `scripts/c2_bpat_pudl_ferc714_ba_code_lookup.py`: fixed `v2026.10.0`, read-only DuckDB `httpfs` S3 or HTTPS access to public `out_ferc714__summarized_demand.parquet`; filter annual records from 2020 through 2025 by the **EIA BA short code `BPAT`** and require source-category `respondent_type='balancing_authority'` for any returned candidate. Output derived CSV and SHA-256 plus exact SQL, source URL, explicit false statuses for original Parquet SHA, operator XLSX, independent respondent approval, hourly demand validation and model training. A source absence or query failure leaves an explanatory JSON.
- `tests/test_c2_bpat_pudl_ferc714_ba_code_lookup.py`: six unit tests.
- `.github/workflows/c2-bpat-pudl-ferc714-remote-coverage.yml`: runs these tests and looks for BA-code evidence independently of earlier name-only candidate lookup, with S3 then HTTPS fallback. The final evidence check requires at least one real nonempty provenance-linked result from *either* strategy. Non-successful name HTTPS fallback is now non-fatal if real BA-code results are obtained.

## Actual execution

An exact local source/test mirror was created; **six of six tests actually passed** using **mocked DuckDB returns**, 0 errors/0 failures. Test output did not read actual PUDL Parquet or confirm an actual BPA identity. Independently delivered reproducible offline local ZIP: `C2_BPAT_PUDL_FERC714_BA_Code_Identity_Discovery_2026_11_25.zip` (4,469 bytes), SHA-256 `4996228b83a87a4190224e5f0d48d6234dffc5848a59159c27d6953ffa58e3b7`, including source, local tests, README and input-file hash manifest. Local tests were run under a dummy `duckdb` import stub for simulated connection requests. GitHub CI push-run status **has not been verified**, as the app run lookup only reports associated PR-triggered runs; do not report a CI green result.

## Critical source status and interpretation

Original public PUDL v2026.10.0 Parquet bytes were **not** retrieved in the assistant environment (S3/HTTPS DNS unavailable), and no genuine BPAT respondent ID was verified from real published rows. The `out` annual table's respondent-to-BA links are **PUDL-curated**, potentially based on EIA861 annual classification and repairs. Therefore these source links are not an independently authenticated BPA operator-original FERC identity, and the `out` annual demand values must **never** be compared to EIA930 as unprocessed original FERC observations.

The next empirical gate is to inspect an actual Actions candidate CSV (with fixed release, SQL and output SHA) and independently review BPAT identity; only then query the **non-imputed `core_ferc714__hourly_planning_area_demand`** for a confirmed respondent, with UTC/timezone/DST and source-vintage gates. Existing authentic BPAT EIA930 52,608 h source is retained. Historical geography, load-weighted exposure, source-vintage/holdout and climate/SSP/PyPSA modeling admission remain BLOCKED. **C-1 frozen and untouched.**
