---
dataset_id: DC-kalro-kilifi-crops
dataset_name: KALRO Kilifi crop knowledge base (yield bands, planting triggers, risk rules)
version: 0.1.0
status: draft
data_source_tag: derived
source_url: https://github.com/Desmond-Mariita/keragita-farm-intelligence
collection_method: Literature compilation (KALRO Mtwapa publications), adapted verbatim from the production platform config
date_range: KALRO Mtwapa 2019 publications; adapted 2026-07-07
geographic_scope: Kilifi County, Kenya (Gongoni Ward sandy soils)
temporal_resolution: static reference (per-season constants)
phase: 4
known_limitations:
  - Literature-based, not measured on the Keragita farm; basis field is "literature" for every crop
  - Gongoni reduction percentages are expert ranges, not fitted estimates
  - KALRO bands describe recommended-practice trials; smallholder realised yields are typically lower
  - Season month windows (masika MAM, vuli OND) are climatological; actual onset varies by year
intended_use:
  - Priors for the Phase-4 thin-data hierarchical yield model (LINV-006 wide priors)
  - Planting-trigger and waterlogging rule exercises in the agro-met module
  - NOT a substitute for farm-recorded seasons; posterior updates must come from data
---

# KALRO Kilifi crop knowledge base

## Description

Nine coastal-Kenya crops (maize, green grams, cowpeas, cassava, watermelon, cashew,
sesame, pigeon pea, sorghum) with KALRO base-yield bands, Gongoni sandy-soil reduction
ranges, P2O5 demand, rainfall/soil-moisture planting triggers, and waterlogging risk
rules. Lives at `config/crops/kilifi_crops.yaml`.

## Source

Adapted verbatim from `keragita-farm-intelligence/config/crops/kilifi_crops.yaml` (the
production platform), which compiled it from KALRO Mtwapa 2019 publications and the
Kilifi County Annual Report. Every crop entry carries `basis` and `kalro_reference`
provenance fields (LINV-007).

## Processing

None — reference constants. Any change to a band or threshold requires a documented
source in the entry's `kalro_reference`/`notes` and a version bump here.

## Validation plan

Phase 4: compare KALRO prior bands against realised Keragita seasons as they accumulate;
the hierarchical model's posterior shrinkage quantifies how informative the priors were.
