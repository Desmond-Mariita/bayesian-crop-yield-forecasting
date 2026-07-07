# Learning Resources — Bayesian Crop Yield Forecasting

**For:** Desmond Momanyi Mariita
**Adapted from:** `keragita-farm-intelligence/docs/learning-resources.md` (the programme's
master list), re-keyed to this repo's four phases.
**Last updated:** 2026-07-07

Search for all resources by the exact title and author listed. URLs are omitted
deliberately — they rot. Search the title.

---

## Spanning the whole programme

Acquire before Phase 2 and keep as references throughout.

| Title | Author | Notes |
|-------|--------|-------|
| Statistical Rethinking (2nd ed, 2020) | Richard McElreath | **The single most important book in this programme.** Bayesian reasoning through examples. Read alongside Phase 2. |
| Bayesian Analysis with Python (3rd ed) | Osvaldo Martin | Directly uses PyMC and ArviZ — the practical companion for the "rebuild in PyMC" half of the charter. |
| Bayesian Data Analysis (3rd ed, BDA3) | Gelman, Carlin, Stern, Dunson, Vehtari, Rubin | The authoritative reference; free PDF on Gelman's site. Chapters as needed, never linearly. |
| Pattern Recognition and Machine Learning | Christopher Bishop | Formal reference; use for lookup. |

**Video:** McElreath's *Statistical Rethinking 2023* lecture series (YouTube, free, ~20h)
— watch alongside the book. Bookmark the *PyMC Labs* channel permanently.

**Documentation:** PyMC docs (Getting Started + Core Notebooks before Phase 2); ArviZ
docs — study the plot gallery and know what each plot tells you.

---

## Phase 1 — Data engineering, statistics, anomaly detection, agro-met (Feb–Apr)

| Resource | Notes |
|----------|-------|
| Think Stats / OpenIntro Statistics | Free online; refresher backdrop for the from-scratch statistics modules. |
| "Robust statistics" — median/MAD literature | Search "median absolute deviation robust outlier detection"; grounds `src/anomaly/` (the production Tier-A detector is a MAD compound rule). |
| FAO Irrigation and Drainage Paper 56 — Crop Evapotranspiration | Allen et al; free FAO PDF. **The** reference for the `src/agromet/` ET0 module (Hargreaves-Samani and, later, Penman-Monteith). |
| "CHIRPS: Rainfall estimates from rain gauge and satellite observations" | Funk et al (2015). Read before Phase 4's Kilifi track, skim now — know the product's limitations. |
| NASA POWER agroclimatology validation papers | Search "NASA POWER agricultural validation". Know what you're joining to NASS. |

## Phase 2 — Bayesian milestones (May–Jul)

**Warm-up (before any sampler code), in order:**
1. Think Bayes (Downey, free online) — ch. 1–4. One week.
2. Ben Lambert's *A Student's Guide to Bayesian Statistics* YouTube series — first 20
   videos. One week.
3. Statistical Rethinking ch. 1–4 + McElreath 2023 lectures 1–4.
4. Watch two different "MCMC explained" videos before writing the Metropolis sampler.
5. "Visualization in Bayesian workflow" (Gabry, Simpson, Vehtari et al, 2019, JRSS-A) —
   **do not skip**; it is the difference between diagnosing a model and being confused
   by it.

**M2a — hierarchical yield model:**

| Resource | Notes |
|----------|-------|
| Statistical Rethinking ch. 13–14 + 2023 lectures 12–14 | The multilevel chapters — read before building. |
| Data Analysis Using Regression and Multilevel/Hierarchical Models — Gelman & Hill | Ch. 11–13; the intuition of partial pooling. |
| "Understanding predictive information criteria for Bayesian models" — Gelman, Hwang, Vehtari (2014) | Behind WAIC; read after the first model comparison. |
| Doing Bayesian Data Analysis — Kruschke | Thorough on MCMC diagnostics; what convergence actually means. |

**M2b — state-space/Kalman:**

| Resource | Notes |
|----------|-------|
| Kalman Filter series — Michel van Biezen (YouTube, ~20 shorts) | The clearest intuitive explanation. Watch before any code. |
| Bayesian Filtering and Smoothing — Simo Särkkä | Free PDF on Särkkä's site; ch. 1–6 essential. The definitive Bayesian treatment. |
| PRML ch. 13 — Bishop | Linear dynamical systems, rigorously. |
| "State Space Models in PyMC" — PyMC Labs (YouTube) | For the rebuild half. |

**M2c — discrete-time survival:**

| Resource | Notes |
|----------|-------|
| Discrete-time survival analysis tutorials | Search "discrete time survival analysis logistic hazard". The production livestock model is exactly this (deliberately not Cox at thin data volumes). |
| BDA3 — relevant survival/GLM sections | Reference as needed. |

## Phase 3 — Deep learning + Bayesian DL prerequisites (Aug–Oct)

| Resource | Notes |
|----------|-------|
| Neural Networks: Zero to Hero — Andrej Karpathy (YouTube) | From-scratch backprop intuition; matches the charter exactly. |
| Deep Learning — Goodfellow, Bengio, Courville | Free online; lookup reference. |
| Probabilistic Deep Learning — Dürr, Sick, Zbinden | The most practical book on uncertainty in NNs; MC Dropout and calibration. Read before the Bayesian-DL weeks. |
| "Dropout as a Bayesian Approximation" — Gal & Ghahramani (2016, ICML) | Why MC Dropout is legitimate, not a hack. |
| "What Uncertainties Do We Need in Bayesian Deep Learning for Computer Vision?" — Kendall & Gal (2017) | The epistemic/aleatoric distinction, rigorously. |
| "On Calibration of Modern Neural Networks" — Guo et al (2017, ICML) | Temperature scaling and ECE — you will implement both from scratch. |
| Uncertainty in Deep Learning (PhD thesis) — Yarin Gal | Free PDF; ch. 2–4 when going deeper. |

## Phase 4 — XAI + Kilifi capstone (Nov–Dec)

| Resource | Notes |
|----------|-------|
| Interpretable Machine Learning — Christoph Molnar | Free online; the standard XAI reference. Ch. on feature importance, SHAP, counterfactuals. |
| "A Unified Approach to Interpreting Model Predictions" — Lundberg & Lee (2017, NeurIPS) | The SHAP paper — read the paper, not just the docs. |
| "Human evaluation of models built for interpretability" — Doshi-Velez & Kim (2017) | Explanations must work for the farm manager, not just the modeller — the production platform's core XAI constraint. |
| KALRO research publications (kalro.org) | Maize/green-gram/cowpea varieties for coastal Kenya — the priors in `kilifi_crops.yaml` come from here. |
| Kenya Meteorological Department seasonal outlooks | Understand the MAM (masika) and OND (vuli) seasons the capstone models operate in. |
| "Precision agriculture in sub-Saharan Africa" literature | Search "digital agriculture smallholder Kenya"; 3–5 recent papers for deployment context. |

---

## Later / production-platform track (post-programme)

For operating `keragita-farm-intelligence` itself: *Designing Machine Learning Systems*
(Chip Huyen, ch. 1–7), "Hidden Technical Debt in Machine Learning Systems" (Sculley et
al, 2015), and the platform's own `docs/` (INVARIANTS, ADR-008, RULES_OF_ENGAGEMENT).
