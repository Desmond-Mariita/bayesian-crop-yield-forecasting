# Internal exploration report — KFI docs survey (subagent: kfi-docs-map, Sonnet)

**Date:** 2026-07-06
**Task:** Survey the `docs/` tree of `Desmond-Mariita/keragita-farm-intelligence` (cloned at
scratchpad `kfi/`) to ground the borrow-analysis in
`reports/analysis/2026-07-06-kfi-borrow-analysis.md`.

---

The platform is built in numbered milestones (M0→M10 + lettered sub-milestones). Each
milestone emits an ADR (decisions), a SPEC (frozen contract), an ACCEPTANCE_CHECKLIST
(numbered ACs with test locations), guides, and data/model cards. Fourteen platform
invariants (INV-001…014, `docs/INVARIANTS.md`) are the spine everything cites.

## 1. Probabilistic models & domain-logic ADRs

**`docs/adr/ADR-008-m4-probabilistic-models.md`** (Accepted, 1145 lines) — core Bayesian ADR. M4 is the first probabilistic milestone; each model activates on an evidence gate, not a date. Four models, all **PyMC**:
- Sensor fusion — state-space/DLM + GP spatial layer; **EC & soil-moisture jointly modelled** (bivariate latent, Cholesky covariance, INV-007); Penman-Monteith ET₀ with propagated uncertainty. Gate: hardware + ≥1 stream. Reject <0.40.
- Crop meta-analysis — hierarchical Bayesian, partial pooling, KALRO yield priors. Gate: ≥3 seasons. Reject <0.50.
- Livestock — discrete-time Bernoulli survival (30-day) + linear mixed-effects. Gate: ≥50 animals AND ≥6mo AND ≥10 vet-confirmed. Reject <0.50.
- Ration optimization — Bayesian stochastic programming (Dirichlet proportions, LP as `pm.Potential` soft penalties). Gate: ≥1 feed batch. Reject <0.45.

Convergence gate: R-hat<1.01, bulk/tail-ESS>400, 0 divergences; wide priors until data (INV-008). Decisions 1–4/8 are the event-sourcing infra that unblocks the models (replay projector DEF-010, calibration state machine DEF-011/023, typed `manual_app` DEF-012, out-of-order weather buffering DEF-013, stock_consumed fix DEF-004).

**XAI (Decision 7):** every model inherits `BayesianModelBase` (extends `XAIBase`), exposing one `explain_or_reject() -> ExplanationCard | RejectionCard`. **ExplanationCard** = dual-audience: `plain_summary` (farm manager) + `technical_detail` dict (investors), plus confidence, data_quality (complete/partial/degraded), model_version, feature_pipeline_version, convergence_flags, prior_summary, data_source. **RejectionCard** = rejection_code (LOW_CONFIDENCE/MISSING_DATA/SENSOR_OFFLINE), missing_sensors, missing_requirements, recommendation. Below-gate → RejectionCard(MISSING_DATA), logged to the append-only decision log, never forced (INV-004). Six explainers for sensor fusion; missing data is first-class via `FeatureBundle.present` bools, never imputed (INV-005). Governance (Decision 10): per-model cards with `status: approved` enforced at load; CI gates check_model_cards / check_xai_interface / check_data_cards. **FAMACHA is deferred (DEF-005 → M5).**

**`docs/adr/ADR-003-m1-weather-soil-crop.md`** (515 lines) — deterministic pre-Bayesian rules, typed `operations_tooling`. CHIRPS/NASA-POWER/Open-Meteo three-provider fallback; **Hargreaves-Samani ET₀** (±5mm/day); **Lindsay 1979 pH-dependent P** (Olsen 6.14ppm → ~2.5–3.0ppm effective at pH 7.64); crop-specific KALRO Mtwapa yield reductions (maize 30–50%, cassava 15–25%); 5-day/60mm green-gram waterlogging window. Every output carries `RecommendationConfidence` (prior_weight=1.0, English+Swahili) — the bridge to M4's ExplanationCard.

**`docs/adr/ADR-005-m2-livestock-operational-intelligence.md`** (518 lines) — deterministic livestock ops (~10 goats, below Bayesian gate). Explicit `deworming_record` event (decoupled from consumable filtering); full vaccination dose history (PPR/CCPP/FMD/Brucellosis); binary **consanguinity_risk flag** (ancestor intersection to 3 gens, deliberately not Wright's F); admin-curated sentinels (7d vs 30d cadence); alert suppression (time-bounded/indefinite, mandatory reason); seasonal anomaly adjustment deferred. Theme: build correct event taxonomy now as Bayesian training data.

## 2. Data cards (`docs/data_cards/`)
YAML-frontmatter + markdown, one per dataset. Schema fields: dataset_name/id, version, schema_version, data_source (+ data_source_tag), status, source_url, collection_method, date_range, geographic_scope, spatial/temporal_resolution, record_count, data_quality, known_limitations[], calibration_status, intended_use[], milestone; body = Description/Source/Processing/Validation Plan.
- **`docs/data_cards/DC-chirps-weather.md`** — CHIRPS v2.0 daily rainfall for Gongoni cell (-2.9863,40.0454), 0.05°(~5.5km), 2020–26; flags convective underestimation, no on-farm gauge; planned 90-day Davis VP2 cross-validation.
- **`docs/data_cards/anomaly_detector_v2.md`** — detector card (draft, approved:false). Rules: `compound_mad` (2+ features, 2.0 MAD, min 5 obs), `clinical_override_heartwater` (critical), `clinical_override_coccidiosis` (major); `seasonal_adjustment` DEFERRED. Flags FAMACHA (DEF-005), EC/soil-moisture pending lab.
- Others: DC-cropnuts-soil, DC-davis-vp2-weather, DC-dragino-lse01-soil, DC-nasapower-weather, DC-openmeteo-forecast, DC-livestock-manual, DC-2025-backfill, public_stats_orbital.yaml.

## 3. Contracts / checklists / policy
- **`docs/contracts/`** (24 `M{N}_SPEC.md`) — frozen implementation contract per milestone (`Status: FROZEN` + freeze note listing applied external reviews); components, event registry, schemas, endpoints, numbered normative clauses. Large (M9=183KB). No edits without a waiver.
- **`docs/checklists/`** (25 `M{N}_ACCEPTANCE_CHECKLIST.yaml`) — each criterion: id (AC-M{N}-NNN), description, category, test_type (unit/integration/negative), test_location (exact `file::Class::method`), deferral_ref, pass_condition (literal pytest cmd exiting 0). M4 = 94 criteria. Cross-checked against SPEC by a spec↔checklist gate.
- **`docs/policy/DEVICE_UNBIND_PROCEDURE.md`** (only policy file) — device-unbind authority matrix (admin/farm_admin/manager/worker) enforced at a named endpoint; cited in the farm's device-insurance application.

## 4. Development / review process
- **`docs/RULES_OF_ENGAGEMENT.md`** (v4.3, 625 lines) — authoritative. Two-loop workflow (Loop 1 Design→ADR+SPEC+checklist frozen after external review; Loop 2 Build→code+3-test rule+docs+governance cards+phase report). Model tiering (haiku=extraction, sonnet=reviews/code, opus=on request). Five right-first-time gates. Single-pass class-based remediation (§4): findings grouped by SYSTEM FAILURE CLASS → plan → 4 parallel critiques → Desmond approval gate → execute → VERDICT w/ class-closure ledger. External reviews run by Desmond (Gemini/GPT/Codex), never Claude. Includes Autonomous Council Mode (overnight codex→gemini→full-quorum, 8-review cap).
- **`docs/INTERNAL_REVIEW_AGENTS.md`** (v3.4, 983 lines) — paired internal agents, 2-at-a-time. Loop 1: Bayesian Design, XAI Contract, Governance, Implementation, Consistency, Operational Validity. Loop 2: Spec Fidelity, Adversarial Security, Governance Enforcer, Test Quality, Data Source, Operational Validity, solo Red Team (12 attack scenarios). Numbered criteria (AS1–19, TQ1–11, SF1–11); each finding needs a failing test + code fix. Codex Principal audit after all pairs. v3.4 gap analysis wires each externally-caught M6a miss to a new criterion (notably the real-migration-harness rule: tests must run the real `apply_m*` chain, not synthetic schemas).
- **`docs/DOCUMENTATION_ROADMAP.md`** (112 lines) — living per-milestone doc index (PLANNED/DRAFT/REVIEWED/COMPLETE) + 2026-05-09 doc-vs-code delta audit.

## 5. Evidence-capture practice (`docs/pilot/`, `docs/reports/`)
- **`docs/pilot/`** — Gongoni field pilot: training scripts (manager, Swahili worker), paper-fallback protocol, sandbox provisioning/seed-data, stage-0/1 checklists. `tickets/` = 17 numbered field bugs (TICKET-001…017). `stage2/` = runbooks, redaction rules, route/evidence manifests. `evidence/` = ISO-timestamped bundles (e.g. `m4_manager_loop_20260509T075026Z/` with herd-risk/yield-outlook/ration-recommendation/sensor-status JSON + markdown report; stage0/1 carry screenshots + migration logs).
- **`docs/reports/`** — per-milestone `m{N}_phase_report.md` (phase-gate PASS/FAIL artifact) + timestamped E2E/QA dirs (ceo-smoke, e2e-walk, phase-a with 10 scene subdirs of screenshots+Playwright traces, verify-ui). Plus `PILOT_COMPLETION_EVIDENCE.md`, `MULTI_FARM_PREPAREDNESS.md`, and `RED_TEAM_2026-06-27.md` — live-droplet review that found+fixed a CRITICAL: calibration + M4 inference routes lacked an auth dependency and took the actor from a forgeable request body (a calibration-poisoning vector against the Bayesian models).

Pattern throughout: evidence lives in ISO-timestamped dirs bundling machine-readable JSON + a human markdown report + screenshots/traces — reviewer reads the report, not the raw run.

## 6. Domain-knowledge docs (mostly `docs/guides/`)
**Key finding: NO KEBS content anywhere in the repo.** Vet-licensing appears only as role authority (vet authorises drugs / milk-withdrawal gates); the only statutory regime encoded is **KDPA** (Kenya Data Protection Act).

Livestock health: `docs/guides/M0-livestock-health-guide.md` (BCS 1.0–5.0, **FAMACHA 1–5, deworm-at-≥3, bottle-jaw**, season disease calendar, heartwater/coccidiosis overrides); `M0-breed-baselines.md` (SEA/Galla/Cross baselines, THI 84/80/82); `M0-anomaly-alert-reference.md` (compound MAD, seasonal modifiers 0.85×/0.90×); `M2-deworming-scheduler-reference.md` (kid/weaner 90d, yearling 180d, adult 365d); `M2-vaccination-tracker-reference.md` (PPR 365d, CCPP 365d, FMD 180d, Brucellosis 365d); `M2-breeding-analytics-reference.md`, `M2-sentinel-protocol-reference.md`, `M2-livestock-rules-reference.md`, `M2-anomaly-detector-refinements.md`, `M2-alert-suppression-reference.md`.

Soil/weather: `docs/guides/M05-soil-baseline.md` (CropNuts CN-404064: **pH 7.64, EC 0.29 dS/m non-saline (supersedes old 0.85 black-cotton), Olsen P 6.14ppm** — INV-014 ground truth); `M1-soil-model-card.md` (Lindsay lookup); `M1-weather-pipeline-guide.md`; `M1-assumption-register.md` (48 hardcoded assumptions: Masika [3,4,5]/Vuli [10,11,12], KALRO yields, THI, helminth-surge 200mm/30d, drought 14d).

Agronomy/crop: `docs/guides/M1-crop-lookup-guide.md` (9 Kilifi crops), `M1-crop-weather-recommendation-guide.md` (8 weather-alert rules + planting calendar), `M7-agronomy-overview.md`, `M7-experimentation-protocol.md` (trial governance).

Economics/feed: `docs/guides/M7-feed-runway-operations.md` (dry-matter demand, silage chain, manure N/P/K offset), `M35-feed-resource-accountability.md`, `M15-economics-guide.md` (KES), `M15-stock-tracking-guide.md`.

Compliance: `docs/guides/M10-kdpa-tenant-export-ops.md` (**KDPA 2019** export right, 7-year retention); `docs/management/{PRODUCT_VISION,PRD}.md` (Veterinarian authorises drug treatments linked to **withdrawal periods + milk-safety gates**; withdrawal override restricted to vet/authorised manager).

Also domain-bearing at top level: `docs/INVARIANTS.md`, `docs/management/{PRD,PRODUCT_VISION,GAP_ANALYSIS}.md`, and the raw soil-lab PDF `docs/Keragita Farms Ltd-Soil Analysis-02 Apr 2026-0219 to 0219.pdf`.
