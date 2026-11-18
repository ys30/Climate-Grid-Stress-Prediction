# C-2 E1 — Why NLR county hourly historical electricity demand is a modeled benchmark, NOT an independent validation target (2026-11-17)

## Verified published external source

- National Laboratory of the Rockies (formerly NREL): *Hourly Electricity Demand Profiles for Each County in the Contiguous United States*, DOI **10.25984/3366592**, https://data.openei.org/submissions/8562; mirrored in official US government data catalog https://catalog.data.gov/dataset/hourly-electricity-demand-profiles-for-each-county-in-the-contiguous-united-states .
- Historical **2016–2023**, estimated hourly demand; official downloadable HDF5 `historic_load_hourly_2016_2023_county.h5`, `https://data.openei.org/files/8562/historic_load_hourly_2016_2023_county.h5`. Time index UTC **hour ending**, county columns `p<5-digit county FIPS>`, MW.
- Open code `https://github.com/NatLabRockies/HistoricalLoadData`, repository main HEAD observed **`06d09b2a426b8606acae1bbe6edb8bb708c11ecb`** at discovery; do not use floating main for pinned formal reproducibility.
- Original dataset website explicitly documents a **2026-02-09 correction** of erroneous distributed PV county attribution. Download actual H5 and hash it before analysis; the file was **not downloaded or inspected in this report**.

## Explicit modeled spatial methodology and circularity

Official dataset documentation states that *county annual retail sales* are **estimated** by first aggregating utility-reported sales at the STATE level and then distributing them to counties by **county share of state population**. County hourly profiles also incorporate weighted BA or subregion reported hourly demand, plus modeled county/sector DPV profiles, direct-use electricity and on-site DPV assumptions.

It is therefore not independent metered county consumption, nor an observed utility-specific county sales allocation. When evaluating E1 county population vs territory weighted ERA5 exposure, correlation with this NLR county demand model can show **sensitivity or consistency between modeling frameworks**, but is not an out-of-sample empirical validation of county electricity-meter fractions. Further, the dataset reuses BA load series, so using it for target/feature validation of EIA-930 derived BA demand risks **target leakage/circularity**. Explicitly segregate from the sealed 2024–25 demand test.

## Scientific admission

| Source | What it supports | What it cannot independently prove |
|---|---|---|
| PUDL fixed v2026.10.0 annual EIA-861 Sales | actual utility/BA/state/sector reported selected MWh | utility×county MWh allocation |
| PUDL fixed service territory | year-specific service-county FIPS membership | county metered MWh or BA operational polygon |
| NLR estimated county hourly demand 2016–2023 | externally modeled, population-informed and BA-informed sensitivity comparison | independent county demand observations / independent BA load out-of-sample validation |

For a mathematically defensible E1 result independent of modeled NLR allocations, quantify *partial identification* from actual original annual utility MWh and the set of source counties: a one-county source can be conditionally assigned if **service FIPS completeness and source sales territory assumptions hold**, while multiple counties have nonnegative shares adding to the source unit's annual MWh and unknown counties stay unidentified. Such per-county bounds are **conditional marginal ranges**, not directly observed county load fractions. In particular do not sum different county upper bounds as if jointly achievable.

No hourly demand training or evaluation approved. `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `GEO_LOAD_RELEVANCE=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`, `model_training_permitted=false`; C-1 frozen.

Sources: https://catalog.data.gov/dataset/hourly-electricity-demand-profiles-for-each-county-in-the-contiguous-united-states ; https://www.eia.gov/tools/faqs/faq.php?id=448&t=1 ; https://www.eia.gov/electricity/data/eia861/ .
