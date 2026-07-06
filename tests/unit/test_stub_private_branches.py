"""Contract tests for stub branches the public-surface sweep cannot reach.

Covers the private stub methods behind dispatch branches (e.g. ``fit`` choosing between
closed-form and gradient descent) and the already-implemented constructor validation.
Same graduation rule as ``test_stub_contracts.py``: when one of these is implemented,
replace its contract test with real unit tests.
"""

import importlib

import numpy as np
import pytest

from src.models.linear_regression import LinearRegression
from src.models.logistic_regression import LogisticRegression
from src.models.regularized import LassoRegression
from src.preprocessing.imputers import SimpleImputer

X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
Y = np.array([1.0, 2.0, 3.0])

SCAFFOLD_PACKAGES = (
    "src.bayesian",
    "src.neural",
    "src.pipeline",
    "src.reporting",
    "src.visualization",
)


@pytest.mark.parametrize("method", ["closed_form", "gradient_descent"])
def test_linear_regression_both_fit_paths_are_stubs(method: str) -> None:
    """Both fit dispatch branches terminate in NotImplementedError stubs."""
    with pytest.raises(NotImplementedError):
        LinearRegression(method=method).fit(X, Y)


def test_logistic_regression_private_stubs() -> None:
    """The sigmoid and loss helpers are stubs."""
    model = LogisticRegression()
    with pytest.raises(NotImplementedError):
        model._sigmoid(Y)
    with pytest.raises(NotImplementedError):
        model._compute_loss(Y, Y)


def test_lasso_soft_threshold_is_a_stub() -> None:
    """The soft-thresholding operator is a stub."""
    with pytest.raises(NotImplementedError):
        LassoRegression()._soft_threshold(1.5, 0.5)


def test_simple_imputer_rejects_unknown_strategy() -> None:
    """Constructor validation is implemented: unknown strategies raise ValueError."""
    with pytest.raises(ValueError, match="Strategy"):
        SimpleImputer(strategy="bogus")


@pytest.mark.parametrize("package_name", SCAFFOLD_PACKAGES)
def test_scaffold_packages_import(package_name: str) -> None:
    """Empty scaffold packages import cleanly and carry a version."""
    package = importlib.import_module(package_name)
    assert package.__version__ == "0.1.0"
