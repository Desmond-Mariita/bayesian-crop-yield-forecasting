# BayesRisk

**Crop Yield Forecasting with Uncertainty Quantification — from scratch**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

BayesRisk is a county-level crop yield forecasting system that combines:
- **Statistical foundations** — rigorous data engineering and hypothesis testing
- **Bayesian inference** — prediction intervals and uncertainty quantification for yield forecasts
- **Deep learning** — neural networks for nonlinear weather–yield interactions

All core algorithms are implemented **from scratch** using only NumPy,
demonstrating deep understanding of the underlying mathematics.

Why yield forecasting? Agricultural forecasts drive planting, insurance, and food-security
decisions, and a point estimate is not enough — decision-makers need calibrated
uncertainty ("90% chance yield falls between X and Y"). That makes this a natural
showcase for Bayesian methods rather than a bolted-on exercise.

## 📊 Dataset

The dataset is assembled (Phase 1) from two public sources:

- **[USDA NASS Quick Stats](https://quickstats.nass.usda.gov/)** — county-level corn and
  soybean yields (bu/acre), harvested acres, and irrigation practice, via the free API.
- **Public weather data** ([NOAA](https://www.ncdc.noaa.gov/cdo-web/) / [PRISM](https://prism.oregonstate.edu/)) —
  county-aggregated growing-season temperature, precipitation, and derived stress
  indicators (growing degree days, dry spells).

Joined on county × year, this yields decades of observations across thousands of
counties, with genuine missingness, outliers (drought years), and mixed
categorical/numeric features — exactly what the preprocessing modules are built for.

**Prediction targets:**
- *Regression:* yield in bu/acre (`yield_bu_per_acre`)
- *Classification:* low-yield event — a season falling significantly below the county's
  historical trend (`low_yield`)

## 📁 Project Structure

```
bayesrisk/
├── src/                    # Source code
│   ├── data/              # NASS/weather acquisition, loading, joining
│   ├── preprocessing/     # Encoders, scalers, imputers, outlier handling
│   ├── statistics/        # Descriptive stats, hypothesis tests, correlation
│   ├── models/            # Linear, logistic, regularized models (from scratch)
│   ├── metrics/           # Evaluation metrics
│   ├── model_selection/   # Cross-validation
│   ├── bayesian/          # Bayesian inference (Phase 2)
│   ├── neural/            # Neural networks (Phase 3)
│   └── pipeline/          # End-to-end pipelines
├── data/                   # Data directory
│   ├── raw/               # Original NASS and weather downloads
│   ├── interim/           # Intermediate data
│   └── processed/         # Final county × year dataset
├── notebooks/              # Jupyter notebooks
├── reports/                # Generated reports
├── tests/                  # Unit and integration tests
└── docs/                   # Documentation
```

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-github-username/bayesrisk.git
cd bayesrisk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

## 🛠️ Implementation Phases

| Phase | Period | Focus | Status |
|-------|--------|-------|--------|
| 1 | Months 1–3 | Data Engineering & Statistical Foundations | 🔄 In Progress |
| 2 | Months 4–6 | Bayesian Yield Modeling & Prediction Intervals | ⏳ Planned |
| 3 | Months 7–9 | Deep Learning from Scratch | ⏳ Planned |

**Phase 1** builds the dataset (NASS + weather join) and implements imputation,
encoding, scaling, hypothesis tests (e.g., irrigated vs. rain-fed yield differences),
and baseline linear/logistic/regularized models — all in NumPy.

**Phase 2** replaces point estimates with posterior distributions: Bayesian linear
regression, hierarchical county-level effects, and calibrated prediction intervals
for yield forecasts.

**Phase 3** implements a neural network from scratch (manual backpropagation) to
capture nonlinear weather–yield interactions, and compares it honestly against the
Bayesian baselines on both accuracy and calibration.

## 📝 Research Log

See [research_log.md](research_log.md) for weekly progress updates.

## 👤 Author

**Desmond Momanyi Mariita**
- Email: dmariita@keragita.com
- LinkedIn: [Your LinkedIn]
- GitHub: [@your-github-username](https://github.com/your-github-username)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- USDA National Agricultural Statistics Service for the Quick Stats API
- NOAA / PRISM Climate Group for public weather data
- University of Potsdam - MSc Cognitive Systems program
