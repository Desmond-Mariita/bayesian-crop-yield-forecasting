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

This project implements all core algorithms **from scratch** using only NumPy,
demonstrating a deep understanding of the underlying mathematics.

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
│   └── visualization/     # Plotting and reporting
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

## 📊 Dataset

This project forecasts crop yields from **weather, soil, and historical-yield** features.
<!-- TODO: confirm the specific dataset source (e.g. FAOSTAT / USDA NASS / a Kaggle crop-yield dataset). -->

## 🛠️ Implementation Phases

| Phase | Period | Focus | Status |
|-------|--------|-------|--------|
| 1 | Feb–Apr | Data Engineering & Statistical Foundations | 🔄 In Progress |
| 2 | May–Jul | Bayesian Statistics Mastery (uncertainty quantification) | ⏳ Planned |
| 3 | Aug–Oct | Deep Learning from Scratch | ⏳ Planned |
| 4 | Nov–Dec | XAI Integration | ⏳ Planned |

## ✅ Quality & Verification

Every change is gated **from commit one** by a git pre-commit hook and CI
(`.github/workflows/ci.yml`):
- **Developer guidelines** (`tools/check_guidelines.py`): Google-style docstrings, PEP 484
  type hints, no `print`, imports at top — per `docs/DEVELOPER_GUIDELINES.txt`.
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
