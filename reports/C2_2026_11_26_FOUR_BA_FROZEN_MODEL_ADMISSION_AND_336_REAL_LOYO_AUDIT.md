# C-2: frozen exploratory model admission and real 336-fit LOYO audit — 2026-11-26

This turn performed a **new actual audit**, reading the 336-row output of the verified original-EIA930/ERA5 four BA LOYO experiment. Exact CSV SHA-256: `41af7c24fd536c5d652f3cf39302499e9870c473d833fb98902375c91f31f0f1`. Historical source ZIP SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504` and source gzip SHA `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac` were inherited from the earlier verified extraction. These are **descriptive original-source analyses**, not independent predictive model validation.

**Actually verified**: 336 rows, 48 unique BA×season×metric×QA configurations, precisely 7 rows each (one full fit and each of 6 calendar-year deletion fits), 288 deletion fits, no duplicates, each deletion reduces days, all fit values finite and in-file slope differences reconcile with the full model. Source flag `weather_mask_approved=False`, `causal=False` in all rows. The smallest omitted-year estimation cohort retains **742 complete UTC days**; the maximum absolute deviation in the reported *cold association coefficient* from its corresponding all-year value across all estimators is **56.225 MW/°C**. This maximum is a *deletion sensitivity diagnostic*, not a prediction error, and occurs in an unqualified weather proxy model.

**Decisive interpretation check**: the LOYO script fits on each reduced cohort and calculates residual RMSE **on those same retained days**. It **never predicts the year that was omitted**, therefore any claim of time-out-of-sample validation, held-out predictive skill or generalization must be removed. The 2025 year had been repeatedly inspected in this project and cannot be described as a sealed blind test.

The machine-readable locked protocol at `protocols/C2_FOUR_BA_MODEL_ADMISSION_V1_20261126.json` defines:
- Four BA (AZPS/BPAT/CISO/SRP), 2020–25; UTC days requiring 24 actual EIA930 demand and 24 candidate ERA5 temperature hours.
- Main descriptive pressure: daily maximum; mandatory robustness: daily intraday P95; distinct mean demand co-outcome.
- Month-year-centered cold and warm hinge exposure with season interactions (Nov–Mar vs Apr–Oct), **not temperature causal effects**.
- Immutable original-source baseline; source flags, independently screened unflagged spike family, and ±1 review-day envelopes restricted to *sensitivity analyses*. No cleaning merely to improve fit.
- Causal inference/model training **blocked** until historical BA operating geography and alternative weather masks, vintage spikes, independent FERC714 respondent21 demand validation and event/year-level statistical dependence are resolved.
- Future predictive validation requires an independently sealed prospective or new-data cohort, not the reused and inspected 2025 sample, and training-only preprocessing to avoid leakage.
- Future CMIP6 SSP and PyPSA outcomes blocked. **C-1 frozen**.

**Local reproducibility**: audited exact real 336-row CSV and saved `REAL_336_LOYO_ADMISSION_AUDIT.json`. Executed five local contract tests, 5/5 passed; ZIP CRC checked, file `C2_20261126_Frozen_Model_Admission_Protocol_And_Real_336_Audit.zip`, SHA-256 `feb34f8f068d6957d99644285f9ea66026a31dd5f8e42f0136066618e9ed89dc`. Includes the original 336-row SHA-verified output, local audit code, machine-readable protocol, JSON actual audit, test code/log, README. Source upstream archive is referenced, not duplicated.

**Important**: the local audit script was actually executed; this report and JSON protocol are committed directly to GitHub. GitHub CI not independently confirmed. No new causal coefficient or FERC hourly observation is claimed.
