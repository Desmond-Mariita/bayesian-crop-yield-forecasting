"""
Correlation analysis implemented from scratch.

This module provides correlation methods without using scipy.

Mathematical Background:
------------------------
Pearson Correlation:
    r_xy = Σ(xᵢ - x̄)(yᵢ - ȳ) / [√Σ(xᵢ - x̄)² * √Σ(yᵢ - ȳ)²]

Spearman Rank Correlation:
    ρ = 1 - (6 * Σdᵢ²) / (n(n² - 1))
    where dᵢ = rank(xᵢ) - rank(yᵢ)

Variance Inflation Factor:
    VIF_j = 1 / (1 - R_j²)
    where R_j² is R² from regressing feature j on all others.
"""

import numpy as np


def pearson_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate Pearson correlation coefficient.

    Formula:
        r = Σ(xᵢ - x̄)(yᵢ - ȳ) / [√Σ(xᵢ - x̄)² * √Σ(yᵢ - ȳ)²]

    Properties:
        - r ∈ [-1, 1]
        - r = 1: Perfect positive linear relationship
        - r = -1: Perfect negative linear relationship
        - r = 0: No linear relationship

    Args:
        x: First variable array.
        y: Second variable array.

    Returns:
        Pearson correlation coefficient.

    Raises:
        ValueError: If arrays have different lengths.
    """
    # TODO: Implement in Week 5
    raise NotImplementedError("Implement this function in Week 5")


def spearman_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate Spearman rank correlation coefficient.

    This is Pearson correlation on the ranks, making it robust
    to outliers and non-linear monotonic relationships.

    Formula:
        ρ = 1 - (6 * Σdᵢ²) / (n(n² - 1))

    Args:
        x: First variable array.
        y: Second variable array.

    Returns:
        Spearman correlation coefficient.
    """
    # TODO: Implement in Week 5
    raise NotImplementedError("Implement this function in Week 5")


def correlation_matrix(X: np.ndarray) -> np.ndarray:
    """
    Compute correlation matrix for all features.

    Args:
        X: Data matrix of shape (n_samples, n_features).

    Returns:
        Correlation matrix of shape (n_features, n_features).
    """
    # TODO: Implement in Week 5
    raise NotImplementedError("Implement this function in Week 5")


def calculate_vif(X: np.ndarray, feature_index: int) -> float:
    """
    Calculate Variance Inflation Factor for a single feature.

    Formula: VIF_j = 1 / (1 - R_j²)

    Interpretation:
        - VIF = 1: No multicollinearity
        - VIF > 5: Moderate multicollinearity
        - VIF > 10: Severe multicollinearity

    In yield modeling:
        High VIF between 'total_precipitation' and 'dry_spell_days'
        suggests they carry similar information about water stress.

    Args:
        X: Data matrix of shape (n_samples, n_features).
        feature_index: Index of the feature to calculate VIF for.

    Returns:
        VIF value.
    """
    # TODO: Implement in Week 5
    # Hint: Regress feature j on all other features, compute R²
    raise NotImplementedError("Implement this function in Week 5")
