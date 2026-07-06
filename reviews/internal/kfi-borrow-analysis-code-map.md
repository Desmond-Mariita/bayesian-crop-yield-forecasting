# Internal exploration report — KFI code map (subagent: kfi-code-map, Sonnet)

**Date:** 2026-07-06
**Task:** Map the `keragita/` package of `Desmond-Mariita/keragita-farm-intelligence` (cloned
at scratchpad `kfi/`) to ground the borrow-analysis in
`reports/analysis/2026-07-06-kfi-borrow-analysis.md`.

---

Package is `src/keragita/` (~130k LOC, 40+ subpackages). Single-process FastAPI + SQLite,
strictly event-sourced farm-intelligence platform for a goat/crop farm in Gongoni/Kilifi,
coastal Kenya. Analytics come in **two tiers**: cheap deterministic rule engines and a
governed PyMC Bayesian tier behind evidence gates + an XAI contract.

## 1. Top-level layout (LOC, biggest first)
- `api/` + `routes/` (~48k): FastAPI HTTP surface (admin/farm_admin/platform_admin, milestone slices m3_5/m4/m8/m9/m10).
- `events/` (12k): event-sourcing core — store, registry, payload schemas, versioning, ingest, central projector, barriers, quarantine, scope guard, reserved-producer gate.
- `models/` (9.6k): the M4 Bayesian tier — 4 PyMC models + base contract, gate evaluator, feature pipelines, explainers.
- `db/` (9.6k): `schema.sql`, `repository.py` (low-level writer), alembic migrations.
- `projectors/` (7.5k): M4/M9/M10 read-model projectors, weather buffer, calibration state machine, tenant caches.
- `dairy/` (6.7k): M8 raw-milk/KEBS regulatory lifecycle, drug-withdrawal registry, transfer lineage.
- `materialisation/` + `materialisers/` (9.2k): cursor-driven read-model engine + M3.5 feed/accountability materialisers & rule scanners.
- `weather/` (1.6k), `adapters/` (3.1k): ingestion (below).
- `anomaly/` (0.9k), `livestock/` (3.0k), `disease/`/`et0/`/`soil/`/`calibration/`/`sensor_health/` (0.3–0.7k each): rule + physical math.
- Support: `auth/`, `middleware/` (shadow-write cutover, tenant routing), `alerts/`, `economics/`, `saas/`, `recall/`, `tasks/`. Bayesian `governance/` schemas live at repo root.

## 2. Statistical / analytical components

**Tier A — deterministic rules (NOT Bayesian):**
- Livestock anomaly detector `anomaly/detector.py:37`: per-animal, life-stage-stratified **modified z-score using median + MAD**, `z=|obs−median|/MAD`, threshold `2.0×seasonal_modifier`. **Compound rule** — fires only when ≥2 features anomalous. Clinical **overrides** (`anomaly/overrides.py`) for heartwater/coccidiosis bypass it. Baselines `anomaly/baselines.py:27` = rolling 20-obs window, MAD floored at 1.0, reset on life-stage change. Features: `weight_kg`, `temperature_c`, `bcs`, `famacha` (anaemia 1–5). Seasonal tightening `anomaly/seasonal.py:50`.
- Weather-triggered disease/crop rules `disease/weather_rules.py` (WTA-001…008): consecutive-day/cumulative-window thresholds.
- Climate indices `disease/indices.py`: **THI** (NRC, breed thresholds SEA 84/Galla 80/Cross 82) and **SPI-1** rainfall anomaly.

**Tier B — physical/agronomic math:**
- ET0 `et0/compute.py`: **FAO-56 Hargreaves-Samani** (`compute_ra` extraterrestrial radiation from lat+Julian day; `0.0023·(Tmean+17.8)·√(Tmax−Tmin)·Ra`, ±5 mm band).
- Soil water balance `soil/water_balance.py`: daily VWC bucket model with Hermite-smoothstep moisture factor gating P uptake, 14-day warm-up.
- Phosphorus `soil/p_model.py`: **Lindsay (1979) pH-dependent P availability** (peak ~pH 6.5), anchored to CropNuts CN-404064 (Olsen P 6.14 ppm, pH 7.64).
- Calibration `calibration/bias_correction.py`: shadow↔production pairing, admin-approval gate, RMSE trailing-drift auto-deactivation.

**Tier C — M4 Bayesian tier (`models/`, PyMC+ArviZ):** All inherit `BayesianModelBase` (`models/bayesian_model_base.py:376`). Core is an **XAI contract**: `explain_or_reject()` returns an `ExplanationCard` (plain_summary + posterior/priors/convergence) or a first-class `RejectionCard` (MISSING_DATA / LOW_CONFIDENCE / SENSOR_OFFLINE) — never raises, never None (INV-004). Each has an **evidence gate** (`models/gate_evaluator.py`, counts events) + **convergence gate** (R-hat<1.01, ESS>400, 0 divergences). Two carry hard **deployment locks** (sensor_fusion, livestock) because they still use placeholder `observed` data (posterior==prior).
- Sensor fusion `models/sensor_fusion/model.py:116`: state-space **DLM**, bivariate EC+soil-moisture latent state, **LKJ Cholesky** covariance; EC prior Normal(0.29,0.20) dS/m; missing channels skip Kalman update but pass presence indicator. Gate: hardware deployed + ≥1 stream; confidence = channel-present fraction (floor 0.40).
- Crop meta-analysis `models/crop_meta_analysis/model.py:105`: **hierarchical partial pooling**, non-centred; KALRO maize prior mu_yield~Normal(2500,1000) kg/ha; rainfall+EC coefficients; **LOO-CV**→confidence. Gate ≥3 seasons.
- Livestock survival `models/livestock_bayesian/model.py:97`: **discrete-time Bernoulli survival** (explicitly NOT Cox), log-linear hazard, survival S(t)=(1−p)^t at 30/60/90d. Gate ≥50 animals AND ≥6mo AND ≥10 vet outcomes; confidence = 1−HDI95 width.
- Ration optimization `models/ration_optimization/model.py`: constrained feed optimization (threshold 0.45).

## 3. Event-sourcing (maintainer must understand)
- Store: `db/schema.sql` `events` table **strictly append-only** (triggers RAISE(ABORT) on UPDATE/DELETE). Envelope: `event_offset` (AUTOINCREMENT PK = global total order), `id` (UUID idempotency key), `event_class` (domain/derived/system), `farm_id` (NOT NULL tenancy), `payload` JSON, `schema_version`, `correlation_id`.
- Append: `events/ingest.py` `insert_domain_event()` → validation pipeline (farm-scope fail-close → reserved-producer gate → registry class → payload validation → SHA-256 **fingerprint dedup** → barriers → backdate ceiling) → `db/repository.py` INSERT.
- Registry/versioning: `events/registry.py` (type→class, type→Pydantic model); `events/versions.py` = **strict append-only allowlist** of (type, schema_version), no identity fallback. Migration = **versioned coexistence** (old versions frozen+readable), not rewrite.
- Projections/replay: `events/projector.py`, `projectors/projector.py`, `materialisation/engine.py` — all replay-based, offset-ordered, idempotent via **offset-gated upserts** (`WHERE last_event_offset < excluded...` = last-wins). Bootstrap wipes+replays 0→HEAD; incremental resumes from `projection_checkpoints`. **INV-015**: projectors pure — no now()/uuid4(), never write back to events. Effective-now = `materialisation_tick` event, not wall-clock.
- Barriers `events/projector_barrier.py`: block authority-dependent writes until projection catches up (HTTP 409/503).
- Decision log `events/payloads/decision.py`: every model/rule decision → `decision_recorded` event → projection-only `decisions` table; captures decision_mode, evidence `input_event_offsets`, and **requires model_version+feature_pipeline_version when probabilistic** (INV-009). Deterministic SHA-256 decision_id → replay-stable.
- Multi-tenancy: `events/scope_guard.py` enforces farm_id at both ingest and low-level writer (fail-closed); `events/reserved_producers.py` frozenset blocks forging sensitive events via generic endpoint; `events/quarantine.py` isolates bad events.

## 4. Ingestion sources
- **CHIRPS** `weather/chirps.py`: HTTPS gzipped GeoTIFF, rainfall only mm (needs rasterio).
- **NASA POWER** `weather/nasapower.py`: HTTPS JSON, temp/RH/solar/wind, no precip.
- **Open-Meteo** `weather/openmeteo.py`: GFS **forecast** (never treated as observation).
- **Davis WeatherLink Live** `adapters/weatherlink_live.py`: on-farm station via **LAN UDP port 22222**; Imperial→metric; dumb producer emitting `weather_packet_received`.
- **Dragino LSE01** `adapters/dragino_lse01.py` + `adapters/mqtt_subscriber.py`: 4 LoRaWAN nodes→ChirpStack→**MQTT**; soil temp/VWC/EC (µS/cm÷1000→dS/m) emitted jointly; EC>3.0→SUSPECT.
- **Manual app**: highest-trust source, never calibration-adjusted (`adapters/utils.py`).
- Selection: `adapters/factory.py` (Hydra config→class, sim↔hardware config-only, per `config/hardware.yaml`); `weather/fallback.py` = 3 capability-specific chains (precip: hardware→CHIRPS→cached; meteorology: hardware→NASA→cached; forecast: Open-Meteo→cached).
- Out-of-order: `projectors/weather_buffer.py` event-time tumbling windows (5-min, keyed on station timestamp, reopen within grace, late→degraded not dropped).
- Synthetic: `adapters/farm_data_generator.py` (seeded), `weather/fixture.py` (JSON test fixtures).

## 5. Config YAMLs
- `config/crops/kilifi_crops.yaml`: 10 coastal crops (maize, green grams, cowpeas, cassava, watermelon, cashew, simsim, pigeon pea, sorghum) w/ Swahili names. Per crop: season (masika=long rains/vuli=short rains), KALRO yield range + Gongoni sandy-soil reduction %, P2O5 demand, planting trigger (rainfall mm+window+min VWC), waterlogging rule (threshold/window/vulnerable stage), risks, KALRO refs. Knowledge base for planting-window/crop-risk advice.
- `config/hardware.yaml`: adapter selection + fallbacks, UDP/MQTT params, 4 Dragino dev-EUI slots, sensor→plot mapping, health cadences (weather 300s/soil 3600s) with STALE>1×/OFFLINE>3×/Tier-3@24h.

## 6. Testing
- **736 test files, ~230k LOC** (tests > source). Organised by concern: `unit/` (282), `integration/` (353), `red_team/` (36 adversarial), `negative/`, `replay/` (determinism), `governance/` (invariants), `e2e/`, domain folders.
- Fixtures `tests/conftest.py`: session-scoped **in-memory SQLite provisioned via alembic-at-head** (never the real DB), Repository, async FastAPI client. Sets `PYTENSOR_FLAGS` to pure-Python linker so PyMC runs without C headers.
- Worth imitating: autouse fixture repairing two process-global leaks (logger `.disabled` after alembic fileConfig; shadow-write cutover mode) for deterministic full-suite ordering; fixed RNG seed 42 everywhere; `materialisation_tick` clock source; `replay/` tests asserting bootstrap==incremental convergence.

**Skills a maintainer needs**: event-sourcing (append-only stores, projections, replay, idempotency, schema versioning); PyMC/ArviZ (hierarchical pooling, survival, state-space/Kalman, LKJ, LOO-CV, convergence); robust stats (MAD z-scores); FAO-56 agro-met (Hargreaves ET0, water balance, THI/SPI); coastal-Kenya agronomy + goat health (FAMACHA, BCS); IoT stack (UDP, MQTT/LoRaWAN, unit conversions, calibration drift).

Best entry files: `models/bayesian_model_base.py` (contract), `events/ingest.py` + `events/registry.py` (write path), `projectors/projector.py` (replay), `anomaly/detector.py` (rule tier), and the two config YAMLs.
