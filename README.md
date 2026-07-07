# Bayesian Crop Yield Forecasting

**Explainable Crop Yield Forecasting with Uncertainty Quantification**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Desmond-Mariita/bayesian-crop-yield-forecasting/actions/workflows/ci.yml/badge.svg)](https://github.com/Desmond-Mariita/bayesian-crop-yield-forecasting/actions/workflows/ci.yml)

## 🎯 Project Overview

Bayesian Crop Yield Forecasting is a crop-yield prediction system that combines:
- **Bayesian inference** for uncertainty quantification — yield forecasts with calibrated confidence intervals, not just point estimates
- **Deep learning** for complex spatial and temporal pattern recognition
- **Explainable AI (XAI)** for transparent, decision-ready predictions

**Charter — derive by hand, then validate in PyMC.** Every algorithm is first implemented
**from scratch in NumPy** to demonstrate the underlying mathematics; each Bayesian
milestone is then **rebuilt in PyMC/ArviZ and the posteriors compared**. The from-scratch
pass builds understanding; the PyMC pass builds fluency with the production stack.

This repo is the learning foundation for operating
[keragita-farm-intelligence](https://github.com/Desmond-Mariita/keragita-farm-intelligence)
— a production Bayesian farm platform (Kilifi County, Kenya). Its curriculum, model
families (hierarchical yield, state-space, survival), governance contracts
(ExplanationCard/RejectionCard, data & model cards, evidence gates), and datasets are
deliberately mirrored here in miniature. See `docs/INVARIANTS.md` and
`reports/analysis/2026-07-06-kfi-borrow-analysis.md`.

## 📁 Project Structure

```
bayesian-crop-yield-forecasting/
├── src/                    # Source code (algorithms from scratch)
│   ├── data/              # Data loading and acquisition
│   ├── preprocessing/     # Encoders, scalers, imputers
│   ├── statistics/        # Descriptive stats, hypothesis tests, correlation
│   ├── models/            # ML models (linear, regularized, logistic, …)
│   ├── model_selection/   # Cross-validation utilities
│   ├── neural/            # Neural networks
│   ├── pipeline/          # End-to-end pipelines
│   ├── visualization/     # Plotting and reporting
│   └── xai/               # ExplanationCard / RejectionCard + evidence gates
├── tools/                  # verify.py + check_guidelines.py (quality gates)
├── scripts/                # Multi-LLM review wrappers (see AGENTS.md)
├── data/                   # raw / interim / processed
├── notebooks/              # Jupyter notebooks
├── reports/                # Generated reports + verification evidence
├── reviews/                # Saved internal/external review reports
├── tests/                  # Unit and integration tests
└── docs/                   # Documentation (incl. DEVELOPER_GUIDELINES.txt)
```

## 🚀 Quick Start

```bash
git clone https://github.com/Desmond-Mariita/bayesian-crop-yield-forecasting.git
cd bayesian-crop-yield-forecasting

# Create the environment (uv recommended; a plain venv works too)
uv venv && uv pip install -e ".[dev]"

# Run the tests
pytest

# Run the verification harness (guidelines, lint, format, tests + coverage)
python tools/verify.py        # writes reports/verification/<timestamp>.md
```

## 📊 Datasets

Two tracks, both governed by data cards in `docs/data_cards/` (CI-enforced):

1. **Volume track (Phases 1–2 workhorse):** **USDA NASS Quickstats** county-level corn &
   soybean yields + **NASA POWER** weather (temperature, humidity, solar, wind).
   Thousands of county-years — enough data to *see* hierarchical partial pooling and
   convergence diagnostics work.
2. **Thin-data capstone (later, Kilifi track):** **CHIRPS v2.0** rainfall + **NASA POWER**
   for the Keragita farm's grid cell, with **KALRO yield bands** as priors
   (`config/crops/kilifi_crops.yaml`). Deliberately sparse — the wide-priors,
   evidence-gated regime the production platform actually operates in.

## 🛠️ Implementation Phases

| Phase | Period | Focus | Status |
|-------|--------|-------|--------|
| 1 | Feb–Apr | Data engineering, statistical foundations, robust anomaly detection (MAD), agro-met (ET0/THI/SPI) | 🔄 In Progress |
| 2 | May–Jul | Bayesian milestones mirroring production: hierarchical yield, state-space/Kalman, discrete-time survival — NumPy → PyMC → compare | ⏳ Planned |
| 3 | Aug–Oct | Deep Learning from Scratch + Bayesian DL prerequisites (MC Dropout, calibration) | ⏳ Planned |
| 4 | Nov–Dec | XAI Integration & Kilifi capstone | ⏳ Planned |

## ✅ Quality & Verification

Every change is gated **from commit one** by a git pre-commit hook and CI
(`.github/workflows/ci.yml`):
- **Developer guidelines** (`tools/check_guidelines.py`): Google-style docstrings, PEP 484
  type hints, no `print`, imports at top — per `docs/DEVELOPER_GUIDELINES.txt`.
- **Data cards** (`tools/check_data_cards.py`): every dataset ships a governance card in
  `docs/data_cards/` — LINV-005 in `docs/INVARIANTS.md`.
- **Companion notebooks** (`tools/check_notebooks.py`): every implemented curriculum
  module ships an explanatory notebook at the mirrored `notebooks/` path, built from
  `notebooks/TEMPLATE.ipynb` (source displayed via `inspect.getsource`, never copied) —
  LINV-010. CI gates notebook *existence*; content and execution discipline are by
  review until the nbmake gate activates.
- **flake8**, **black**, **mypy** (advisory), and **pytest with a ≥90% coverage gate**.
- **Verification harness** (`tools/verify.py`) runs every gate and writes a timestamped,
  reviewable report to `reports/verification/` with a binary PASS/FAIL verdict.

Independent multi-model code review (DeepSeek, Gemini, Codex, Kimi, GLM) is wired via
`scripts/*_review.sh` — see `AGENTS.md` and `CLAUDE.md`.

## 📝 Research Log

See [research_log.md](research_log.md) for weekly progress updates.

## 👤 Author

**Desmond Momanyi Mariita**
- Email: dmariita@keragita.com
- GitHub: https://github.com/Desmond-Mariita

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Open agricultural / crop-yield data providers
- University of Potsdam — MSc Cognitive Systems program
