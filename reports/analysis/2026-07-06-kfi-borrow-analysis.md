# What to borrow from keragita-farm-intelligence

**Date:** 2026-07-06
**Author:** Claude (orchestrator), from two internal exploration reports of
`Desmond-Mariita/keragita-farm-intelligence` (KFI) @ HEAD, plus direct reads of
`docs/INVARIANTS.md`, `docs/learning-resources.md`, `docs/adr/ADR-008-m4-probabilistic-models.md`,
and `config/crops/kilifi_crops.yaml`.
**Goal:** make this learning repo (`bayesian-crop-yield-forecasting`) prepare its author to
**comfortably manage the KFI production platform**.

---

## 1. Context: what KFI actually is

- Production farm-management platform for Keragita Farms Ltd (6-acre mixed farm, Gongoni
  Ward, Kilifi County, Kenya). FastAPI + SQLite, event-sourced (append-only event log,
  replayable projectors), Svelte PWA, Telegram alerts, $6/mo droplet.
- KFI is **Repo 6** of a six-repo learning programme (`bayes-foundations`,
  `keragita-yield-model`, `keragita-sensor-fusion`, `keragita-xai-toolkit`,
  `keragita-bayesian-dl`, then the platform). This learning repo effectively plays the role
  of Repos 1–2 (+ parts of 5).
- Analytics in two tiers:
  - **Tier A/B (live now):** deterministic rules — MAD-based compound anomaly detection for
    livestock (weight, temperature, BCS, FAMACHA), weather-trigger rules, THI/SPI indices,
    FAO-56 Hargreaves-Samani ET0, soil water balance, Lindsay pH-dependent P availability.
  - **Tier C (M4, gated):** four PyMC Bayesian models — sensor-fusion DLM/state-space
    (bivariate EC+soil-moisture latent state, LKJ Cholesky), hierarchical crop
    meta-analysis with KALRO priors and LOO-CV, discrete-time Bernoulli survival for
    livestock, Bayesian stochastic programming for rations. Convergence gates:
    R-hat < 1.01, ESS > 400, zero divergences.
- Governance is CI-enforced (20 invariants): every model implements
  `explain_or_reject() -> ExplanationCard | RejectionCard`; missing data is a model input
  (never a dropped row); every record tags `data_source`; wide priors until farm data
  accumulates; data cards + model cards (with `prior_justification` and convergence
  diagnostics) are deploy-blocking; replay is deterministic.
- **Skills a KFI maintainer needs** (from code map): event sourcing (projections, replay,
  idempotency, schema versioning); PyMC/ArviZ fluency (hierarchical pooling, survival,
  state-space/Kalman, LKJ, LOO-CV, diagnostics); robust statistics (median/MAD z-scores,
  rolling baselines); FAO-56 agro-meteorology; coastal-Kenya agronomy + goat health
  (FAMACHA, BCS, masika/vuli seasons, KALRO yield bands); IoT ingestion (MQTT/LoRaWAN,
  UDP, calibration drift, multi-provider fallback).

## 2. The headline gap

The learning repo currently targets **US county corn/soybeans (USDA NASS)** with
**from-scratch NumPy only**, and its Phase 2 "Bayesian" plan is generic. KFI needs someone
fluent in **PyMC/ArviZ on thin, messy, Kenyan-coast agricultural data**, operating under an
XAI-and-governance contract. From-scratch NumPy builds the right foundations but, alone,
never touches the production stack, the domain, or the governance discipline.

**Recommendation:** keep the from-scratch pedagogy, but re-point every phase at KFI's
models, data sources, domain constants, and contracts, and add a "graduate to PyMC"
step per milestone ("build it by hand → rebuild in PyMC → compare posteriors").

> **Charter note (Codex finding 3):** this changes the repo's stated identity from
> "from scratch, NumPy only" to "**derive by hand first, then validate/rebuild in PyMC
> for Bayesian milestones**". README.md and research_log.md must be updated to say this
> explicitly, or the plan will contradict the repo's own docs. The PyMC pass is
> validation/reimplementation, not a parallel curriculum.

## 3. Borrow list (prioritised)

> **Re-prioritised after Codex review** (`reviews/codex/kfi-borrow-analysis.md`,
> APPROVE-WITH-CHANGES): P0 is now split into *governance scaffolding* (small, high
> leverage, do first) and *curriculum alignment*; the Kilifi data track moves down to P2
> (capstone-sized, needs the scaffolding first); a lightweight-ops section is added.

### P0a — governance scaffolding (small, high-leverage, do first)
Items 5–8 below (XAI contract, missing-data-as-feature, data/model cards + CI checkers,
learning-repo INVARIANTS.md). These are days-not-weeks of work, immediately unlock the
coverage gate with real tests, and instil the single most KFI-distinctive habits.

### P0b — re-aim the curriculum at the production target
1. **Adopt the six-repo curriculum + reading list.** Copy/adapt KFI
   `docs/learning-resources.md` (McElreath, BDA3, Gelman & Hill, Sarkka, Gal, Molnar; the
   "reading order for the first milestone") into this repo and key each phase of
   `research_log.md` to it.
2. **Mirror KFI's four M4 model families as Phase-2 milestones**, in this order:
   (a) hierarchical partial-pooling yield model with KALRO yield-band priors — the direct
   precursor to KFI's crop meta-analysis; (b) state-space/Kalman filter (precursor to the
   sensor-fusion DLM; Sarkka ch. 1–6); (c) discrete-time Bernoulli survival model
   (KFI livestock model — explicitly *not* Cox); (d) optional: constrained/stochastic
   optimisation (rations). Each milestone: from-scratch NumPy implementation first, then
   the same model in PyMC with ArviZ diagnostics, then a comparison notebook.
3. **Adopt evidence gates as pedagogy.** KFI models activate on evidence gates
   (e.g. ≥3 complete crop seasons), not dates. Give each learning milestone an explicit
   gate ("this model may not be claimed done until R-hat < 1.01, ESS > 400,
   0 divergences, and a model card exists") and implement the gate evaluator +
   convergence checks from scratch as an exercise.
4. **Add a Kilifi data track alongside NASS** *(demoted to P2 per Codex — capstone-sized;
   do after the phase structure and governance scaffolding are stable)*. Wire the same
   free sources KFI uses: CHIRPS v2.0 rainfall (GeoTIFF), NASA POWER (temp/RH/solar/wind),
   Open-Meteo forecasts, for the Gongoni cell (-2.9863, 40.0454). NASS stays for volume
   (many counties/years → good for learning hierarchical pooling); Kilifi is the capstone
   (thin data → wide priors, exactly KFI's INV-008 regime). Copying
   `config/crops/kilifi_crops.yaml` in as a domain-knowledge config is cheap and can
   happen earlier.

### P1 — adopt the production contracts in miniature (see P0a — do these first)
5. **XAI contract from day one.** Port the `explain_or_reject()` idea: every model in
   `src/models/` (even from-scratch linear regression) returns an ExplanationCard
   (plain-language summary + technical detail + confidence + data-quality + versions) or a
   RejectionCard (structured refusal when data/confidence is below gate) — never a bare
   point estimate, never a forced prediction with a warning. This is INV-001/004/009 and
   is the single most distinctive KFI habit.
6. **Missing data as a feature (INV-005).** The imputers module should grow a
   presence-indicator pattern: absence flags fed to models, not silently dropped or
   imputed rows. Exercises: compare posterior behaviour with indicator vs deletion vs
   imputation.
7. **Data cards + model cards, CI-enforced (INV-002/011).** Borrow the KFI card schemas
   (YAML frontmatter: source, method, date range, resolution, known_limitations,
   calibration_status, intended_use; model cards add `prior_justification` and R-hat/ESS/
   divergences). Add `tools/check_data_cards.py` / `check_model_cards.py` to
   `tools/verify.py` so a missing card fails verification — governance by CI, not
   aspiration.
8. **A learning-repo INVARIANTS.md.** Write ~6–8 invariants adapted from KFI (XAI
   first-class; missing-data-as-input; data_source tagging; wide priors on thin data;
   fixed seeds; evidence before claims) and cite them in reviews, exactly as KFI review
   agents cite INV-IDs.

### P2 — borrow the statistics/domain content that Tier A/B runs on
9. **Robust anomaly-detection module** (Phase 1 material): median/MAD modified z-scores,
   rolling 20-obs baselines with MAD floor, compound rules (fire only on ≥2 anomalous
   features), seasonal threshold modifiers, clinical override pattern. This mirrors
   `keragita/anomaly/` almost 1:1 and is ideal from-scratch NumPy content.
10. **Agro-meteorology module:** FAO-56 Hargreaves-Samani ET0 (extraterrestrial radiation
    from latitude + Julian day), Penman-Monteith with uncertainty propagation (the M4
    version), daily soil water-balance bucket model, THI with breed thresholds, SPI.
    Deterministic, unit-testable, directly production-relevant.
11. **Domain constants as config, with provenance.** Borrow the pattern of
    `kilifi_crops.yaml` and KFI's assumption register: every domain number (KALRO yield
    band, waterlogging threshold, EC baseline 0.29 dS/m, masika/vuli months) lives in a
    config file with a `basis`/reference field — no magic numbers, satisfying the existing
    developer guidelines.
12. **EC × soil-moisture joint modelling (INV-007)** as a worked example of "domain
    constraint shapes the model": exercise on why the two must be modelled jointly in
    saline coastal soil (bivariate latent state, LKJ prior).

### P3 — process & evidence practices
13. **Acceptance checklists per milestone** (KFI `docs/checklists/`): numbered criteria,
    each with test type, exact test location, and a literal pytest `pass_condition`
    command. Slot into the existing plan-before-code + verify.py discipline.
14. **Evidence bundles**: ISO-timestamped directories with machine-readable JSON + a human
    markdown report (KFI `docs/pilot/evidence/`). `reports/verification/` already does
    this — extend the same pattern to model-fit evidence (ArviZ plots, posterior
    summaries) per milestone.
15. **ADRs + assumption register + JOURNAL.** Record model/design decisions as short ADRs
    (KFI has 37); keep an assumption register listing every hardcoded assumption with its
    source; `research_log.md` already plays the JOURNAL role.
16. **A miniature event-sourcing exercise** (stretch, Phase 1 or 3): append-only SQLite
    event table + a pure projector + a replay-determinism test (bootstrap == incremental).
    A few hundred lines, teaches the single most KFI-specific architectural skill
    (INV-003/015) without rebuilding the platform. *(Codex: first-cut candidate if time
    runs short — stretch only.)*

### P3+ — lightweight day-2 ops practices (added per Codex finding 2)
Managing KFI is not only modelling. Borrow these **in miniature**, as exercises, without
duplicating the platform:
17. **Backup + restore drill**: KFI ships `deploy/backup.sh` + `deploy/restore-test.sh`
    on a systemd timer. Exercise: script a backup of the learning repo's SQLite/data
    artifacts and prove restore works (restore-test pattern).
18. **Drift/calibration monitoring**: KFI auto-deactivates calibration offsets on RMSE
    trailing drift (`calibration/bias_correction.py`). Exercise: a small drift monitor
    over model residuals with an alert threshold.
19. **Schema-evolution hygiene**: versioned coexistence (old schema versions frozen and
    readable, never rewritten) — apply to this repo's data-file formats; read KFI's
    alembic chain, don't port it.
20. **Runbook + health-check habit**: a `docs/runbook.md` for the learning repo's
    pipelines (how to re-run, where evidence lands, what "healthy" looks like), mirroring
    KFI's deployment checklists/smoke tests in one page.

### Explicitly NOT worth borrowing
- The FastAPI/PWA/multi-tenant/SaaS surface, alembic migration chains, MQTT/UDP adapters,
  KEBS/dairy/recall compliance machinery — platform engineering, not Bayesian learning;
  it would drown the curriculum. (Read the code, don't port it. Lightweight ops practices
  are carved out above per Codex.)
- KFI's heavyweight two-loop review bureaucracy — this repo already has a leaner
  wrapper-based review protocol.

## 4. Scope realism (Codex check 4)
The full list is **overloaded for 9 months part-time**. Cut order if time runs short:
(1) ration/constrained-optimisation milestone 2(d); (2) the miniature event-sourcing
exercise; (3) the full Kilifi acquisition track (keep the crops YAML + thin-data capstone
concept, defer the CHIRPS/GeoTIFF plumbing). The governance scaffolding and the three core
Bayesian milestones (hierarchical, state-space, survival) are the non-negotiable spine.

## 5. Concrete next steps (atomised per Codex finding 4; 1–2 atomic tasks each)
1. **Charter update** (1 task): rewrite README.md + research_log.md preamble to the
   "derive by hand → validate/rebuild in PyMC" charter.
2. **Governance scaffold, part 1** (2 tasks): add `docs/INVARIANTS.md` (learning-repo
   invariants); implement ExplanationCard/RejectionCard dataclasses + gate-evaluator with
   tests (first real coverage-gate tests).
3. **Governance scaffold, part 2** (2 tasks): add data-card/model-card schemas +
   `tools/check_data_cards.py` wired into `tools/verify.py`; write the first data card
   (NASS).
4. **Curriculum rewrite** (1 task): rewrite the `research_log.md` phase plan — Phase 1
   adds anomaly-detection + agro-met modules; Phase 2 = three KFI-mirroring Bayesian
   milestones (hierarchical / state-space / survival) with evidence gates; Phase 3 keys
   to `keragita-bayesian-dl` prerequisites (MC Dropout, calibration,
   epistemic/aleatoric). Import an adapted `docs/learning-resources.md`.
5. **Domain config** (1 task): adapt `config/crops/kilifi_crops.yaml` into `config/` with
   provenance fields.
6. **Later, gated on the above**: CHIRPS/NASA-POWER acquisition in
   `src/data/acquisition.py`; lightweight ops exercises (backup/restore drill, drift
   monitor, runbook).
