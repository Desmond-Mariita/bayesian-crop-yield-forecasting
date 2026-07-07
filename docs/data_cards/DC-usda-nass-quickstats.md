---
dataset_id: DC-usda-nass-quickstats
dataset_name: USDA NASS Quickstats county yields
version: 0.1.0
status: draft
data_source_tag: api_nass
source_url: https://quickstats.nass.usda.gov/api
collection_method: REST API pull (annual survey statistics)
date_range: 1990-2025 (planned pull window; matches the code default year_start=1990)
geographic_scope: US counties (corn belt states first)
temporal_resolution: annual (county-year)
phase: 1
known_limitations:
  - Survey-based estimates, not measurements; small counties are suppressed or noisy
  - County boundaries and reporting coverage change across years
  - Yield is reported in bu/acre; unit conversion to t/ha must be explicit and tested
  - Weather is not included; joined separately from NASA POWER (see future card)
intended_use:
  - Volume track for learning: descriptive statistics, regression, cross-validation
  - Hierarchical partial-pooling yield model (Phase 2, milestone 2a)
  - NOT for Kilifi/Keragita inference — domain transfer is a capstone question
---

# USDA NASS Quickstats — county corn & soybean yields

## Description

Annual county-level yield statistics for corn and soybeans from the USDA National
Agricultural Statistics Service Quickstats API. This is the repo's **volume track**
dataset: thousands of county-years, enough to make hierarchical pooling and convergence
diagnostics visible while learning.

## Source

Quickstats REST API (`https://quickstats.nass.usda.gov/api`). Requires a free API key
(`NASS_API_KEY` environment variable, never committed). Pull is implemented in
`src/data/acquisition.py::download_nass_yields` (implemented 2026-07-07; county-level
survey yields, suppressed values kept as NaN, every row tagged `api_nass`; companion
notebook `notebooks/data/acquisition.ipynb`).

## Processing

Planned: raw JSON → `data/raw/`, tidied county-year table → `data/processed/`, with the
`data_source` column set to `api_nass` on every record (LINV-005 companion practice;
tagging mirrors production INV-006).

## Validation plan

Cross-check a sample of county-years against the NASS web UI; assert unit conversions
round-trip; record pull date and query parameters in the processing log.
