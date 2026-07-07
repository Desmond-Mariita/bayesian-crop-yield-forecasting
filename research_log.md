# Bayesian Crop Yield Forecasting Research Log

**Author:** Desmond Momanyi Mariita  
**Domain:** Crop yield forecasting — USDA NASS + NASA POWER (volume track), CHIRPS +
KALRO priors for the Keragita/Kilifi capstone (thin-data track)  
**Goal:** Statistical, Bayesian, and deep learning mastery over Feb–Dec (three 3-month
core phases + a 2-month XAI/capstone phase), sufficient to comfortably operate the
`keragita-farm-intelligence` production platform  
**Charter:** derive every algorithm by hand (NumPy) first; rebuild each Bayesian
milestone in PyMC/ArviZ and compare posteriors. Governance mirrors production in
miniature: `docs/INVARIANTS.md`, data/model cards, ExplanationCard/RejectionCard,
evidence gates. (Rationale: `reports/analysis/2026-07-06-kfi-borrow-analysis.md`.)

**Graduation rule (per module):** implementation + real unit tests (replacing the stub
contract) + companion notebook at the mirrored `notebooks/` path (LINV-010) — all in the
same week. Reading plan: `docs/learning-resources.md`.

---

## Progress Overview

| Phase | Period | Status | Completion |
|-------|--------|--------|------------|
| Phase 1: Data Engineering & Statistical Foundations (+ anomaly detection, agro-met) | Feb–Apr | 🔄 In Progress | 0% |
| Phase 2: Bayesian Modeling — hierarchical / state-space / survival (NumPy → PyMC) | May–Jul | ⏳ Not Started | 0% |
| Phase 3: Deep Learning from Scratch + Bayesian DL prerequisites | Aug–Oct | ⏳ Not Started | 0% |
| Phase 4: XAI Integration & Kilifi Capstone | Nov–Dec | ⏳ Not Started | 0% |

---

# Milestone Plan

Mirrors the production platform's model families and gate discipline. Every Bayesian
milestone has an **evidence gate** (may not start before it) and a **convergence gate**
(may not be claimed done before it — R-hat < 1.01, bulk/tail ESS > 400, 0 divergences,
per `src/xai/gates.py`).

## Phase 1 — Data Engineering & Statistical Foundations (Feb–Apr)

The stub TODO markers in `src/` pin the week numbers (e.g. descriptive stats → Week 4,
closed-form linear regression → Week 9).

| Weeks | Milestone | Modules |
|-------|-----------|---------|
| 1–2 | NASS acquisition + loading; data card first (LINV-005) | `src/data/` |
| 3–5 | Descriptive stats, correlation/VIF, hypothesis tests | `src/statistics/` |
| 6–8 | Preprocessing with **missing-data indicators, not deletion** (LINV-004); metrics | `src/preprocessing/`, `src/metrics/` |
| 9–11 | Linear (closed-form + GD), logistic, ridge/lasso, cross-validation | `src/models/`, `src/model_selection/` |
| 12–13 | **New — production Tier-A/B mirrors:** robust anomaly detection (median/MAD modified z-scores, rolling baselines, compound ≥2-feature rules, seasonal modifiers) and agro-meteorology (FAO-56 Hargreaves-Samani ET0, THI, SPI) | `src/anomaly/`, `src/agromet/` (new) |

**Phase exit gate:** every Phase-1 stub graduated (tests + notebooks), NASA POWER weather
joined to NASS with `data_source` tags, `tools/verify.py` PASS.

## Phase 2 — Bayesian Modeling (May–Jul), NumPy → PyMC → compare

Each milestone follows the same loop: (1) derive and implement by hand — including the
diagnostics (own R-hat and ESS implementations before trusting ArviZ's); (2) rebuild the
same model in PyMC; (3) a comparison notebook showing the posteriors agree; (4) model
card with `prior_justification` and diagnostics (LINV-005/006).

| Milestone | Model (production counterpart) | Evidence gate | Core skills |
|-----------|-------------------------------|---------------|-------------|
| M2a (wks 14–18) | **Hierarchical partial-pooling yield model** on NASS county-years (crop meta-analysis) | Phase-1 pipeline complete; ≥ 500 county-year rows loaded | Conjugate/grid warm-up, Metropolis sampler from scratch, non-centred parameterisation, shrinkage, LOO/WAIC concept |
| M2b (wks 19–22) | **State-space / Kalman filter** on weather series (sensor-fusion DLM) | M2a done | Filter + smoother by hand, missing observations as partial updates (LINV-004), then PyMC DLM |
| M2c (wks 23–26) | **Discrete-time Bernoulli survival** on simulated herd data, seeded (livestock model) | M2b done | Hazard h(t)=1−exp(−λ(t)), log-linear covariates, censoring, S(t) curves |

Every model integrates `src/xai`: gate check first, `ExplanationCard` or `RejectionCard`
always (LINV-001..003). *Stretch only (first cut if time runs short): Bayesian ration
optimisation; miniature event-sourcing exercise.*

## Phase 3 — Deep Learning + Bayesian DL prerequisites (Aug–Oct)

MLP + backprop from scratch → then the `keragita-bayesian-dl` prerequisites: MC Dropout
as approximate Bayesian inference (Gal & Ghahramani), calibration from scratch (ECE,
reliability diagrams, temperature scaling), epistemic vs aleatoric uncertainty
(Kendall & Gal).

## Phase 4 — XAI Integration & Kilifi Capstone (Nov–Dec)

- CHIRPS + NASA POWER acquisition for the Gongoni cell (-2.9863, 40.0454), with data
  cards; adapt `kilifi_crops.yaml` (KALRO yield bands as priors, provenance fields).
- **Thin-data capstone:** the M2a hierarchical model re-aimed at 1–3 Kilifi seasons —
  wide priors (LINV-006), evidence gates unmet by design at first, `RejectionCard`s as
  honest output. This is the regime the production platform actually operates in.
- Feature-attribution reading (Molnar) applied to the yield model's explanations.
- Lightweight day-2 ops exercises: backup/restore drill, residual-drift monitor, runbook.

---

# Weekly Log

## Week 1: Environment Setup & Data Acquisition
**Dates:** Feb 3-9, 2026

### Objectives
- [ ] Set up project structure
- [ ] Download and profile dataset
- [ ] Create data loading utilities

### Completed Work

| Date | Task | Time (hrs) | Notes |
|------|------|-----------|-------|
| Mon  |      |           |       |
| Tue  |      |           |       |
| Wed  |      |           |       |
| Thu  |      |           |       |
| Fri  |      |           |       |

**Total Hours:** 0

### Code Written
- `src/data/loader.py` - (Description)

### Key Learnings
- (What did you understand better this week?)

### Challenges Encountered
- (What was difficult? How did you resolve it?)

### Mathematical Concepts Practiced
- (Which formulas did you implement? Any insights?)

### Connection to Transcript Gaps
- (How does this week's work address your identified weaknesses?)

### Blockers for Next Week
- (What might slow you down?)

### Self-Assessment (1-5)
- Confidence in concepts: ___ / 5
- Code quality: ___ / 5
- Documentation completeness: ___ / 5

---

## Week 2: Missing Value Analysis & Imputation
**Dates:** Feb 10-16, 2026

### Objectives
- [ ] Calculate missing value percentages
- [ ] Implement imputation strategies FROM SCRATCH
- [ ] Document decisions

### Completed Work

| Date | Task | Time (hrs) | Notes |
|------|------|-----------|-------|
| Mon  |      |           |       |
| Tue  |      |           |       |
| Wed  |      |           |       |
| Thu  |      |           |       |
| Fri  |      |           |       |

**Total Hours:** 0

### Code Written
- (List files)

### Key Learnings
- 

### Challenges Encountered
- 

### Mathematical Concepts Practiced
- Mean formula: x̄ = (1/n)∑xᵢ

### Self-Assessment (1-5)
- Confidence in concepts: ___ / 5
- Code quality: ___ / 5
- Documentation completeness: ___ / 5

---

<!-- Copy template below for additional weeks -->

## Week N: [Title]
**Dates:** [Start] - [End], 2026

### Objectives
- [ ] Task 1
- [ ] Task 2

### Completed Work

| Date | Task | Time (hrs) | Notes |
|------|------|-----------|-------|
| Mon  |      |           |       |
| Tue  |      |           |       |
| Wed  |      |           |       |
| Thu  |      |           |       |
| Fri  |      |           |       |

**Total Hours:** 0

### Code Written
- (List files)

### Key Learnings
- 

### Challenges Encountered
- 

### Mathematical Concepts Practiced
- 

### Self-Assessment (1-5)
- Confidence in concepts: ___ / 5
- Code quality: ___ / 5
- Documentation completeness: ___ / 5
