"""
Missing value imputation strategies implemented from scratch.

This module provides imputation methods without using sklearn.

Mathematical Background:
------------------------
Mean imputation replaces missing values with the sample mean:
    x̄ = (1/n) * Σᵢ xᵢ

The mean minimizes the sum of squared deviations, making it the
optimal point estimate under squared error loss.
"""

from typing import Optional

import numpy as np

# =============================================================================
# CONSTANTS
# =============================================================================
VALID_STRATEGIES = ["mean", "median", "mode", "constant"]


class SimpleImputer:
    """
    Simple imputation transformer for completing missing values.

    Implements imputation strategies FROM SCRATCH without sklearn.

    Attributes:
        strategy: The imputation strategy ('mean', 'median', 'mode', 'constant').
        fill_value: The value to use when strategy='constant'.
        statistics_: The computed statistics for each feature (after fit).

    Example:
        >>> imputer = SimpleImputer(strategy='mean')
        >>> imputer.fit(X_train)
        >>> X_imputed = imputer.transform(X_test)
    """

    def __init__(
        self,
        strategy: str = "mean",
        fill_value: Optional[float] = None,
    ) -> None:
        """
        Initialize the SimpleImputer.

        Args:
            strategy: Imputation strategy. One of 'mean', 'median', 'mode', 'constant'.
            fill_value: Value to use when strategy is 'constant'.

        Raises:
            ValueError: If strategy is not valid.
        """
        if strategy not in VALID_STRATEGIES:
            raise ValueError(f"Strategy must be one of {VALID_STRATEGIES}")
        self.strategy = strategy
        self.fill_value = fill_value
        self.statistics_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "SimpleImputer":
        """
        Compute the statistics for imputation.

        Args:
            X: Input array of shape (n_samples, n_features).

        Returns:
            self: The fitted imputer.

        Raises:
            ValueError: If X is empty or all values are missing.
        """
        # TODO: Implement in Week 2
        # Remember: NO numpy.mean(), numpy.median() - implement from scratch!
        raise NotImplementedError("Implement this method in Week 2")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Impute missing values in X.

        Args:
            X: Input array of shape (n_samples, n_features).

        Returns:
            X_imputed: Array with missing values imputed.

        Raises:
            RuntimeError: If transform is called before fit.
        """
        # TODO: Implement in Week 2
        raise NotImplementedError("Implement this method in Week 2")

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Fit and transform in one step.

        Args:
            X: Input array of shape (n_samples, n_features).

        Returns:
            X_imputed: Array with missing values imputed.
        """
        return self.fit(X).transform(X)


def calculate_mean_manual(values: np.ndarray) -> float:
    """
    Calculate arithmetic mean manually WITHOUT using np.mean().

    Mathematical formula:
        x̄ = (1/n) * Σᵢ₌₁ⁿ xᵢ

    Why this matters:
        The sample mean minimizes sum of squared deviations,
        making it optimal under squared error loss.

    Args:
        values: 1D array of non-null numeric values.

    Returns:
        The arithmetic mean.

    Raises:
        ValueError: If input array is empty.

    Example:
        >>> calculate_mean_manual(np.array([1, 2, 3, 4, 5]))
        3.0
    """
    # TODO: Implement in Week 2
    # Hint: Use np.sum() and len() or values.shape[0]
    raise NotImplementedError("Implement this function in Week 2")


def calculate_median_manual(values: np.ndarray) -> float:
    """
    Calculate median manually WITHOUT using np.median().

    The median is the middle value when data is sorted.
    For even n, it's the average of the two middle values.

    Args:
        values: 1D array of non-null numeric values.

    Returns:
        The median value.

    Raises:
        ValueError: If input array is empty.
    """
    # TODO: Implement in Week 2
    # Hint: Sort the array first, then find the middle
    raise NotImplementedError("Implement this function in Week 2")
