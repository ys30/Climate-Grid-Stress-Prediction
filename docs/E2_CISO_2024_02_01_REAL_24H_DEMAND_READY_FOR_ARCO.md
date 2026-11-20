# E2 matching UTC-day readiness: real CISO load for public ERA5 24h pilot

## Independent EIA-930 source verification

This document is based on actual source artifact
`c2-eia930-CISO-2024-44427373589` (artifact ID `14486655626`),
previously downloaded from
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44427373589.
The original `utc_start/eia930_CISO_2024_start.csv` was independently reopened
and its SHA-256 recomputed, matching its own provenance manifest exactly:

`375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c`

The CISO 2024 annual EIA demand audit status is `pass: true`.

## Observed CISO demand on 2024-02-01, UTC interval start

All **24/24** hours from `2024-02-01T00:00:00Z` through
`2024-02-01T23:00:00Z` occur exactly once in the authenticated CSV.

- Mean: **24,141.208333 MW**
- Minimum: **20,974 MW**, UTC 12:00
- Maximum: **26,671 MW**, UTC 03:00
- Hourly demand sum: **579,389 MWh**, using 1h intervals
- First hour: UTC start 00:00, demand **23,818 MW**, EIA original HE **2024-02-01T01**
- Last hour: UTC start 23:00, demand **24,109 MW**, EIA original HE **2024-02-02T00**

These are authentic **source-only** EIA load measurements, not forecasts.
Do not infer local time by ignoring daylight-saving changes: the source and
planned weather join are both explicitly keyed to UTC.

## Connection with public ARCO ERA5 day pilot

The public ARCO ERA5 grid-cell pilot targets exactly the same 24 UTC
timestamps but represents **one illustrative grid cell near Sacramento**
(38.5N, 121.5W). It is NOT an approved CISO-wide temperature proxy.

- GitHub workflow: `c2-era5-public-daily-pilot.yml`
- First pilot run:
  https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44678645391
- At time of writing, the source pilot was **queued**.
- Once real observed ERA5 hourly values and SHA manifests are retrieved,
  verify temporal intersection and missingness; a 24-hour point-cell
  *diagnostic comparison* may be performed but cannot establish a CISO-wide
  weather-load relationship or model skill.

The official EIA year-source 23/24 pass accounting is unchanged.
The separate AZPS 2023 noncanonical sensitivity source does not enter this
CISO sample. C-1 frozen study remains untouched.
