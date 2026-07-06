"""
Feature scaling transformations implemented from scratch.

This module provides scaling methods without using sklearn.

Mathematical Background:
------------------------
Standardization (Z-score normalization):
    z = (x - μ) / σ

Min-Max Scaling:
    x_scaled = (x - x_min) / (x_max - x_min)

Box-Cox Transformation (for positive data):
    y^(λ) = (y^λ - 1) / λ    if λ ≠ 0
    y^(λ) = ln(y)            if λ = 0
"""

from typing import Optional, Tuple

import numpy as np


class StandardScaler:
    """
    Standardize features by removing mean and scaling to unit variance.

    Mathematical formula:
        z = (x - μ) / σ

    This transformation results in features with zero mean and unit variance.

    Attributes:
        mean_: Mean of each feature (after fit).
        std_: Standard deviation of each feature (after fit).

    Example:
        >>> scaler = StandardScaler()
        >>> scaler.fit(X_train)
        >>> X_scaled = scaler.transform(X_test)
    """

    def __init__(self) -> None:
        """Initialize the StandardScaler."""
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "StandardScaler":
        """
        Compute the mean and std for scaling.

        Args:
            X: Input array of shape (n_samples, n_features).

        Returns:
            self: The fitted scaler.
        """
        # TODO: Implement in Week 8
        # Remember: Implement mean and std from scratch!
        raise NotImplementedError("Implement this method in Week 8")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Standardize features using computed statistics.

        Args:
            X: Input array of shape (n_samples, n_features).

        Returns:
            X_scaled: Standardized array.
        """
        # TODO: Implement in Week 8
        raise NotImplementedError("Implement this method in Week 8")

    def inverse_transform(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Reverse the standardization.

        Args:
            X_scaled: Standardized array.

        Returns:
            X: Original scale array.
        """
        # TODO: Implement in Week 8
        raise NotImplementedError("Implement this method in Week 8")


class MinMaxScaler:
    """
    Scale features to a given range (default [0, 1]).

    Mathematical formula:
        x_scaled = (x - x_min) / (x_max - x_min)

    Attributes:
        feature_range: Desired range of transformed data.
        min_: Minimum value of each feature.
        max_: Maximum value of each feature.
    """

    def __init__(self, feature_range: Tuple[float, float] = (0, 1)) -> None:
        """
        Initialize the MinMaxScaler.

        Args:
            feature_range: Desired range (min, max) for scaling.
        """
        self.feature_range = feature_range
        self.min_: Optional[np.ndarray] = None
        self.max_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "MinMaxScaler":
        """Compute min and max for scaling.

        Args:
            X: Feature matrix to fit the scaler on.

        Returns:
            The fitted scaler (``self``).
        """
        # TODO: Implement in Week 8
        raise NotImplementedError("Implement this method in Week 8")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Scale features to the specified range.

        Args:
            X: Feature matrix to scale.

        Returns:
            The scaled feature matrix.
        """
        # TODO: Implement in Week 8
        raise NotImplementedError("Implement this method in Week 8")
