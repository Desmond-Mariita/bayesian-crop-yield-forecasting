"""
Categorical encoding strategies implemented from scratch.

This module provides encoding methods without using sklearn.

Mathematical Background:
------------------------
Target Encoding (Mean Encoding):
    x̂ᵢⱼ = (nⱼ * ȳⱼ + m * ȳ) / (nⱼ + m)

Where:
    - nⱼ = count of category j
    - ȳⱼ = mean target for category j
    - m = smoothing parameter
    - ȳ = global target mean

Smoothing prevents overfitting when category counts are low.
"""

from typing import Dict, Optional

import numpy as np


class OneHotEncoder:
    """
    One-hot encoding for categorical variables.

    Transforms categorical features into binary indicator columns.

    Attributes:
        categories_: Dictionary mapping feature index to unique categories.
        drop_first: Whether to drop the first category (avoid dummy trap).

    Example:
        >>> encoder = OneHotEncoder()
        >>> encoder.fit(X_categorical)
        >>> X_encoded = encoder.transform(X_categorical)
    """

    def __init__(self, drop_first: bool = False) -> None:
        """
        Initialize the OneHotEncoder.

        Args:
            drop_first: If True, drop the first category to avoid
                       multicollinearity (dummy variable trap).
        """
        self.drop_first = drop_first
        self.categories_: Optional[Dict[int, np.ndarray]] = None

    def fit(self, X: np.ndarray) -> "OneHotEncoder":
        """
        Learn the categories from the data.

        Args:
            X: Input array of shape (n_samples, n_features).

        Returns:
            self: The fitted encoder.
        """
        # TODO: Implement in Week 3
        raise NotImplementedError("Implement this method in Week 3")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform categorical features to one-hot encoded format.

        Args:
            X: Input array of shape (n_samples, n_features).

        Returns:
            X_encoded: One-hot encoded array.

        Raises:
            RuntimeError: If transform called before fit.
            ValueError: If unknown category encountered.
        """
        # TODO: Implement in Week 3
        raise NotImplementedError("Implement this method in Week 3")


class TargetEncoder:
    """
    Target encoding (mean encoding) with smoothing.

    Encodes categorical variables using target statistics.

    Mathematical formula:
        x̂ᵢⱼ = (nⱼ * ȳⱼ + m * ȳ) / (nⱼ + m)

    The smoothing parameter m prevents overfitting when
    category counts are low by shrinking toward the global mean.

    Attributes:
        smoothing: Smoothing parameter (higher = more regularization).
        encoding_map_: Dictionary mapping categories to encoded values.

    Example:
        >>> encoder = TargetEncoder(smoothing=10)
        >>> encoder.fit(X_train, y_train)
        >>> X_encoded = encoder.transform(X_test)
    """

    def __init__(self, smoothing: float = 10.0) -> None:
        """
        Initialize the TargetEncoder.

        Args:
            smoothing: Smoothing parameter. Higher values shrink
                      category means more toward the global mean.
        """
        self.smoothing = smoothing
        self.global_mean_: Optional[float] = None
        self.encoding_map_: Optional[Dict[str, float]] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "TargetEncoder":
        """
        Learn the encoding from training data.

        Args:
            X: Categorical feature array of shape (n_samples,).
            y: Target array of shape (n_samples,).

        Returns:
            self: The fitted encoder.
        """
        # TODO: Implement in Week 3
        raise NotImplementedError("Implement this method in Week 3")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform categorical feature to encoded values.

        Args:
            X: Categorical feature array.

        Returns:
            X_encoded: Encoded array.
        """
        # TODO: Implement in Week 3
        raise NotImplementedError("Implement this method in Week 3")
