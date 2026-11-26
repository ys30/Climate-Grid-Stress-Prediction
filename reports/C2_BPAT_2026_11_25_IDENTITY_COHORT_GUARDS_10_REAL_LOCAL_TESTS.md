# C-2 BPAT — source identity cohort integrity: exact packaged code retested (2026-11-25)

## What was actually independently verified

The earlier user-delivered `C2_BPAT_PUDL_FERC714_BA_Code_Identity_Discovery_2026_11_25.zip` **was opened from the active runtime**; SHA-256 values of its Python source/test matched the ZIP's source-file manifest, and the six tests inside were actually executed using offline mock DuckDB returns: **6/6 passed**.

The source-only annual BPAT FERC714 code-linkage helper was then corrected to reject (i) duplicate `respondent_id_ferc714` × reporting year, (ii) source rows outside the requested 2020–25 cohort, and (iii) malformed result column-count; (iv) a 2025-only result is explicitly preserved as a one-year source record, **not filled out to six years**. Four new targeted regression tests were executed in the same offline source environment: **10/10 passed**, no failures/errors. The mock import shim is for tests only, not remote data reads. The GitHub source and test files were committed (`01680ca` and `d9a9e5e`).

Independently created and CRC/SHA-validated local ZIP: `C2_BPAT_FERC714_BA_Identity_10_Test_Verified_2026_11_25.zip`; total **5,348 bytes**, SHA-256 `b8c4160aa71d6838eee274a0d1cee08e11be22d9de19d2d1bebfcefae9ae7f1d`. It contains revised code, all 10 tests, original local test log, README and source-file SHA manifest.

## Source discovery status — still blocked

PUDL's official published `out_ferc714__summarized_demand` [table dictionary](https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html) confirms respondent-year identities and `balancing_authority_code_eia`; use **identity metadata only** in this table, never derived/imputed annual demand as independently observed FERC load. The [public data viewer](https://data.catalyst.coop/preview/pudl/out_ferc714__summarized_demand) shows access links and field metadata, not direct BPAT filtered source rows without authenticated access. The assistant's binary S3/HTTPS connection remains unavailable. GitHub connector exposes no comprehensive push-run listing, and public GitHub Actions pages could not be fetched. There is **no verified BPAT FERC respondent ID or source original FERC Parquet SHA**, and **no new FERC-714 numerical comparison**.

Ten locally passing tests attest to behavior on simulated rows; do not claim source availability or GitHub CI green. FERC planning area reporting is not necessarily the identical operational BPAT area. The independent 52,608-hour EIA-930 BPAT 2020–25 observed-demand archive is retained; EIA vintage, true historical operational BA geometry and geography/load weighting remain separate blocked gates. No SSP/PyPSA model training or climate attribution. **C-1 remains frozen and untouched**.
