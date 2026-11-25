# C-2 BPAT — fixed PUDL FERC714 UTC/source-schema hardening (2026-11-25)

## Verified against official release data dictionary

PUDL v2026.10.0 documents both `core_ferc714__respondent_id` (respondent name; PUDL respondent ID; CSV/XBRL native IDs; EIA code) and `core_ferc714__hourly_planning_area_demand` (report date, `datetime_utc`, `demand_mwh`, respondent IDs, time zone). The documentation says PUDL reinterprets source FERC Form 714 hour 1–24 and T24/next-day T00 as UTC datetimes and that the hourly `core` table does **not** contain the extra demand imputations present in the `out` table. Verified against official release docs: https://docs.catalyst.coop/pudl/en/v2026.10.0/data_dictionaries/pudl_db.html .

## Actual correction to committed code

Previously, `scripts/c2_bpat_pudl_ferc714_fixed_release.py` handled offset-aware `datetime_utc` by **stripping its timezone instead of converting the instant to UTC**. A timestamp like `2025-12-31 04:00-08:00` would have been erroneously paired to 04:00 UTC rather than 12:00 UTC. This could generate spurious EIA–FERC source disagreement.

- Introduced `normalize_utc`: offset-aware -> `astimezone(timezone.utc)` -> strip tzinfo only AFTER conversion; naive documented UTC timestamp remains unchanged.
- Reject non-datetime values and non-whole-hour values. Require unique BPA-named candidate respondent identifiers and an EIA mapping value before conditional reviewed-ID audit.
- No-review metadata discovery output explicitly flags `bpa_original_XLSX_verified=false`, `EIA930_full_hourly_comparison_completed=false` and `model_training_permitted=false`.
- Four extra tests specifically cover timezone offset, naive UTC, non-hourly timestamp rejection, and invalid timestamp types, bringing the fixed-release intake suite to **nine committed synthetic test definitions**. GitHub CI status **has not been independently verified**; code submission is not a claim of 9/9 tests passing.

## Persistent scientific restrictions

No original PUDL fixed-release Parquet files have been downloaded and SHA-checked in this analysis turn. Neither the BPA respondent identity nor any 2020–25 FERC respondent hourly readings were empirically verified. GitHub connector can retrieve known runs but provides no comprehensive push-run listing; earlier empty PR-filtered workflow responses cannot prove either completion or failure. BPA's six XLSX originals also have not been authenticated; third-party 12-hour preview remains explicitly unverified.

The `core` FERC714 table's already-normalized UTC timestamps come with PUDL source-cleaning assumptions; even with the conversion fix, respondent identity, native hour-ending clock, time zone/DST, demand definition and original-vintage concordance must still be confirmed before cross-source metrics. Neither PUDL nor FERC714 reports provide geolocated hourly county demand. C-1 frozen; E1/E2 and future SSP/PyPSA model gates remain closed.
