---
dataset_id: DC-nasapower-weather
dataset_name: NASA POWER daily agroclimatology (point)
version: 0.1.0
status: draft
data_source_tag: api_nasa_power
source_url: https://power.larc.nasa.gov/api/temporal/daily/point
collection_method: REST API pull (daily point time series, AG community)
date_range: 1981-present (POWER daily record starts 1981)
geographic_scope: Global 0.5 x 0.625 degree grid; pulled per point (US county centroids now, Gongoni cell -2.9863,40.0454 in Phase 4)
temporal_resolution: daily
phase: 1
known_limitations:
  - Reanalysis-derived (MERRA-2), not station observations; local microclimate is smoothed
  - Coarse ~50 km grid cell; a "county centroid" pull is one cell, not an area average
  - No gauge-quality precipitation product used here; rainfall joins from CHIRPS later
  - Fill value -999 marks missing days; kept as NaN, never dropped (LINV-004)
intended_use:
  - Growing-season weather features joined to NASS county yields (volume track)
  - Same API reused verbatim for the Kilifi capstone weather pull (Phase 4)
  - NOT for site-specific extremes (frost hours, hail) — grid smoothing hides them
---

# NASA POWER — daily agroclimatology, point time series

## Description

Daily temperature (mean/max/min), relative humidity, all-sky solar radiation, and
2 m wind speed for a requested point, from NASA's POWER service (AG community units:
degC, %, MJ m^-2 day^-1, m s^-1). This is the weather half of the volume track, and —
by curriculum decision — the same source the keragita-farm-intelligence platform
consumes, so the acquisition code transfers directly to the Kilifi capstone.

## Source

POWER daily-point REST API (keyless). Pull implemented in
`src/data/acquisition.py::download_weather_data` (implemented 2026-07-08; input
validation before any network use, -999 fills kept as NaN, every row tagged
`api_nasa_power`; companion notebook `notebooks/data/acquisition.ipynb`).

## Processing

Raw JSON → tidy daily table (one row per day, one column per parameter, coordinates on
every row) → `data/raw/nasa_power_daily_<start>_<end>.csv`. Growing-season aggregation
to county-year features is a separate processing step with its own tests.

## Validation plan

Cross-check a sample month against the POWER web viewer; compare summer means against a
NOAA station near a chosen county centroid to quantify reanalysis bias before the yield
model consumes the features.
