# C-2 BPAT — actual EIA numeric ID vs FERC respondent identity contract (2026-11-25)

## Verified external semantics

PUDL v2026.10.0 respondent metadata `core_ferc714__respondent_id` uses a **PUDL-assigned integer** `respondent_id_ferc714`, identifies older CSV and newer XBRL respondent IDs, and has `eia_code` of **EIA numeric utility or balancing-authority ID**, NOT the EIA BA short string `BPAT`. PUDL explicitly cautions utility and balancing authority IDs are not necessarily equal. See: https://data.catalyst.coop/preview/pudl/core_ferc714__respondent_id and https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html .

Therefore earlier tests using synthetic `eia_code='BPAT'` were type-inaccurate. A name match plus nonempty `eia_code` does not prove FERC respondent covers the actual BPAT BA.

## New working identity review artifact

New `scripts/c2_bpat_ferc714_identity_contract.py` requires all these distinct source facts before even declaring the review metadata internally coherent: positive numeric PUDL respondent ID; name BPA candidate; positive numeric `eia_code`; a separately reviewed link repeating the same FERC respondent ID and EIA numeric ID, explicitly asserting `balancing_authority_code_eia='BPAT'`; nonempty public source evidence URL, review date and affirmative review declaration. It rejects `eia_code='BPAT'` and mismatched IDs. Outputs still explicitly say `underlying_evidence_independently_authenticated_by_code=false`, `BPA_original_xlsx_verified=false`, `model_training_permitted=false` and `full_FERC_EIA_comparison_completed=false`. Thus a self-supplied 'review' cannot become scientific certification.

New `tests/test_c2_bpat_ferc714_identity_contract.py` was independently executed in the local Python runtime: **8/8 passed** (synthetic-only fixtures, no real BPA respondent). The actual local source/test code and an offline ZIP are delivered separately. GitHub commits: source `aec569b`, tests `7ebc157`, workflow addition `a5ee8bb`. The S3/HTTPS respondent discovery workflow now also executes these identity tests; no corresponding GitHub CI status or actual query output is authenticated.

## Actual data availability

Current assistant runtime still fails DNS resolution when trying the exact fixed-release public PUDL S3 HTTPS Parquet source. Official source direct download, complete fixed-release original Parquet SHA and bona fide BPA respondent ID remain unverified. Existing 52,608-hour BPAT EIA-930 baseline is genuine but cannot substitute for FERC-714 data. A previously published 12-hour third-party preview remains unverified against BPA XLSX original. **No new observed FERC values, no paired six-year comparison and no operational BA geometry** are claimed.

## Next evidence

Secure a respondent source extract (source query output + fixed release URL/SQL, and ideally original Parquet checksum), then obtain a separately cited mapping to the annual EIA balancing authority code. Recheck respondent roles across 2020–25, then audit unfilled `core_ferc714__hourly_planning_area_demand` UTC hours, hour-ending conventions and area load definitions. Model gates remain closed; **C-1 frozen**.
