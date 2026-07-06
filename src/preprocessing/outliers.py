"""
Outlier detection methods implemented from scratch.

This module provides outlier detection without using sklearn.

Mathematical Background:
------------------------
IQR Method:
    Outlier if x < Q1 - 1.5*IQR or x > Q3 + 1.5*IQR
    where IQR = Q3 - Q1

Z-Score Method:
    Outlier if |z| > threshold (typically 3)
    where z = (x - μ) / σ

Mahalanobis Distance:
    D_M(x) = √((x - μ)ᵀ Σ⁻¹ (x - μ))
    Accounts for correlations between features.
"""

from typing import Tuple

import numpy as np


def detect_outliers_iqr(
    values: np.ndarray,
    multiplier: float = 1.5,
) -> Tuple[np.ndarray, float, float]:
    """
    Detect outliers using the IQR method.

    Mathematical formula:
        Lower bound = Q1 - multiplier * IQR
        Upper bound = Q3 + multiplier * IQR
        where IQR = Q3 - Q1

    Args:
        values: 1D array of numeric values.
        multiplier: IQR multiplier (default 1.5 for standard outliers,
                   use 3.0 for extreme outliers).

    Returns:
        Tuple of (outlier_mask, lower_bound, upper_bound).

    Example:
        >>> mask, lower, upper = detect_outliers_iqr(data)
        >>> outliers = data[mask]
    """
    # TODO: Implement in Week 7
    raise NotImplementedError("Implement this function in Week 7")


def detect_outliers_zscore(
    values: np.ndarray,
    threshold: float = 3.0,
) -> np.ndarray:
    """
    Detect outliers using Z-score method.

    A point is an outlier if |z| > threshold.

    Args:
        values: 1D array of numeric values.
        threshold: Z-score threshold (default 3.0).

    Returns:
        Boolean mask where True indicates outlier.
    """
    # TODO: Implement in Week 7
    raise NotImplementedError("Implement this function in Week 7")


def mahalanobis_distance(X: np.ndarray, point: np.ndarray) -> float:
    """
    Calculate Mahalanobis distance from a point to distribution center.

    Mathematical formula:
        D_M(x) = √((x - μ)ᵀ Σ⁻¹ (x - μ))

    Unlike Euclidean distance, Mahalanobis accounts for correlations
    between features, making it better for detecting multivariate outliers.

    Args:
        X: Data matrix of shape (n_samples, n_features).
        point: Point to calculate distance for, shape (n_features,).

    Returns:
        Mahalanobis distance.

    Example:
        In yield data: a season with very high rainfall but also very
        high drought-stress days is suspicious. Euclidean distance might
        miss this (both values are individually plausible). Mahalanobis
        detects the unusual *combination* given the correlation structure.
    """
    # TODO: Implement in Week 7
    raise NotImplementedError("Implement this function in Week 7")
