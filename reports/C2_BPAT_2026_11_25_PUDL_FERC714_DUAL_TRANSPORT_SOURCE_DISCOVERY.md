# C-2 BPAT — PUDL FERC714 fixed-release dual-transport respondent discovery (2026-11-25)

## Verified external source facts

The [official PUDL v2026.10.0 data access documentation](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_access.html) documents a public `s3://pudl.catalyst.coop` fixed-release bucket, anonymous DuckDB `httpfs` reads, and **path-style** S3 access. Public HTTPS access to the same fixed-release Parquet object can be attempted using the region-specific bucket path-style URL `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.10.0/...`. In either case the read remains a remote curated-data query, *not* a byte-for-byte authenticated download of the complete upstream Parquet file.

The assistant environment could not retrieve actual S3 Parquet bytes, and the connector exposes no searchable listing for GitHub push-triggered workflow runs. A public GitHub Actions page also did not return a usable run listing. **No independently verified actual respondent candidate output, PUDL source SHA, full BPA XLSX original, CI success, or six-year FERC/EIA hour comparison is available in this turn.**

## Submitted code changes

`scripts/c2_bpat_pudl_ferc714_remote_coverage.py` now accepts `--transport s3|https`. Both transports are strictly hard-coded to **v2026.10.0**, the same two non-imputed `core_ferc714` source tables, and unchanged query semantics. S3 creates the documented `REGION 'us-west-2', URL_STYLE 'path'` secret. HTTPS uses the same bucket/object at the public path-style `https://s3.us-west-2.amazonaws.com/` address, relying on DuckDB HTTPS range reads instead of the S3 protocol secret. The output provenance includes transport, exact read URI, SQL and derived candidate CSV SHA.

`tests/test_c2_bpat_pudl_ferc714_remote_coverage.py` adds two mocked offline transport tests: verify HTTPS is fixed-release, does not create S3 secret and uses HTTPS read_parquet; reject disallowed source transport. This raises the module to **seven** test definitions; their GitHub CI run remains **unverified**.

`.github/workflows/c2-bpat-pudl-ferc714-remote-coverage.yml` now tries public S3 first; if that step returns failure, it attempts the **same immutable release via HTTPS** in a new output directory. Both paths are included in always-upload source-only diagnostic artifacts. An S3 failure can still produce a successful workflow **only if the HTTPS fallback succeeds**; no successful run has been observed/verified.

## Next measured decision

Obtain one of the remote query artifacts and examine the real `BPA_FERC714_RESPONDENT_CANDIDATES.csv`; pin derived provenance and independently verify the associated FERC respondent and EIA BA code. Then query 2020–25 actual core-hour coverage for that specific ID and compare UTC source values with the already archived 52,608 EIA930 BPAT demand hours. Cross-source validation remains separate from genuine operator-original XLSX certification, which is still unachieved. The synthetic tests and dual-transport design are **engineering progress, not newly observed BPA data**.

Spatial BA operational geography, geographic demand weights, EIA930 vintage conflicts and inspected 2025 holdout remain unchanged. All model training, climate attribution, CMIP6 SSP and PyPSA stress model gates remain BLOCKED; **C-1 frozen**.
