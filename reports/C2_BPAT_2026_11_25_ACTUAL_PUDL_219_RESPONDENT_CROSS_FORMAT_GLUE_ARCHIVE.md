# C-2 BPAT — AUTHENTIC PUDL FERC-714 CSV↔XBRL respondent mapping archived (2026-11-25)

## First source-byte evidence acquired this stage

**An authentic file was accessed through the connected GitHub repository**, not an assumed S3 download or mocked local fixture:

- PUDL upstream repository: `catalyst-cooperative/pudl`
- Exact source commit: `97874c209147452055842c1d9a5f2614d934be6b`
- Original path: `src/pudl/package_data/glue/respondent_id_ferc714.csv`
- Upstream Git blob SHA-1: `3eb0291e51502df9a5fca38e9f3ac4ebf3526ad7`
- Original contents: header + **219 real respondent mapping rows**. Fields: `respondent_id_ferc714`, `respondent_id_ferc714_xbrl`, `respondent_id_ferc714_csv`, `Source`, `Notes`.
- **119 mapping rows have nonblank XBRL respondent IDs; 100 have blank XBRL IDs.** These are real *row* counts, not claims about 2020–25 BPA coverage.
- Archived byte-identical data in C-2: `data/source_only/PUDL_ferc714_respondent_csv_xbrl_glue_97874c2.csv`, commit `abb126922857be864129ded9e1c0d58645e9d54b`.
- Independently fetched the C-2 archive file through GitHub connector; **its exact blob SHA matched upstream `3eb0291e51502df9a5fca38e9f3ac4ebf3526ad7`**. Therefore source file identity is actually verified, not merely based on filenames.

PUDL's own 2026.10 FERC-714 documentation and transformation source describe this manually maintained cross-CSV/XBRL mapping as one source for its PUDL respondent IDs: https://docs.catalyst.coop/pudl/en/v2026.10.0/data_sources/ferc714.html and https://github.com/catalyst-cooperative/pudl/blob/97874c209147452055842c1d9a5f2614d934be6b/src/pudl/glue/ferc714.py . This file is a **source ID glue table**, not hourly load observations or independent operator identity certification.

## Actual source audit machinery

- New `scripts/c2_bpat_ferc714_pudl_glue_csv_pinned_audit.py` validates **full original git-blob SHA-1 framing**, published schema, unique numeric PUDL IDs, 219 records, and 119/100 XBRL mapped/unmapped split; emits audit JSON with separate SHA-256 and all scientific approval flags false.
- Three local Python source-hash/failure contract tests **actually ran and passed 3/3** in the assistant runtime (known Git blob `hello` hash, wrong raw source rejection, immutable source hash pin). **This is not a verified CI pass or a claim that local tests processed the 219 source bytes.**
- Updated `.github/workflows/c2-bpat-pudl-ferc714-remote-coverage.yml` to use **the actual archived C-2 CSV bytes** for its pinned source audit, rather than download the same CSV from external GitHub, and includes the immutable CSV in workflow path triggers. Source audit may now succeed offline from repository checkout when the S3 respondent-name and annual BPAT-code lookup still fail.
- The workflow's **final BPA source discovery gate remains strict**: glue source success alone does **not** count as obtaining a named or BA-linked BPA respondent. The CI source discovery step still requires a nonempty genuine `BPA_FERC714_RESPONDENT_CANDIDATES.csv` or `PUDL_BPAT_FERC714_YEARLY_RESPONDENT_LINKS.csv`. No run outcome or artifact from the updated workflow was verified.

## Critical scientific interpretation

**This mapping lacks BPA/Bonneville names, EIA numeric ID and `BPAT` BA codes.** Therefore, no observed row can yet be assigned to BPA from this source alone. The absence of XBRL IDs in 100 mappings does **not** mean that BPA lacks 2021–25 observations or that 100 reporters stopped filing: this is a file-level mapping property requiring historical identity cross-reference.

In particular:
- `out_ferc714__summarized_demand` metadata is potentially useful to *identify* BA-linked respondent-year records, but its imputed/derived demand should not be used as original FERC observations.
- `core_ferc714__hourly_planning_area_demand` remains the targeted unfilled FERC hourly series for an eventual 2020–25 BPAT × EIA-930 comparison.
- No fixed-release Parquet original, BPA operator XLSX, authentic BPAT respondent ID, six-year FERC hourly matched values, or historical operator-certified BA geography is newly available here.

**Next evidence gate:** acquire the fixed-release respondent name/EIA-BA association (or pinned independent source that identifies BPA respondent) and join it to this **now authentic, archived cross-era mapping**. Only then fetch and verify FERC hourly data, establish exact UTC/hour-ending semantics, and pair against the existing 52,608 true BPAT EIA930 demand-hour baseline. All training/climate-attribution/SSP/PyPSA model gates remain BLOCKED. **C-1 unchanged and frozen.**
