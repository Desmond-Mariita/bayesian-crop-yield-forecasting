"""
Descriptive statistics implemented from scratch.

This module provides statistical measures without using scipy.stats.

Mathematical Background:
------------------------
Sample Variance (with Bessel's correction):
    s² = (1/(n-1)) * Σᵢ (xᵢ - x̄)²

Why n-1 (Bessel's correction)?
    Using n-1 provides an unbiased estimate of population variance.
    With n, we would systematically underestimate variance.

Skewness (Fisher-Pearson):
    γ₁ = m₃ / m₂^(3/2)
    where mₖ is the k-th central moment
"""

from typing import Tuple

import numpy as np


def calculate_mean(values: np.ndarray) -> float:
    """
    Calculate arithmetic mean.

    Formula: x̄ = (1/n) * Σᵢ xᵢ

    Args:
        values: 1D array of numeric values.

    Returns:
        Arithmetic mean.

    Raises:
        ValueError: If array is empty.
    """
    # TODO: Implement in Week 4
    raise NotImplementedError("Implement this function in Week 4")


def calculate_variance(values: np.ndarray, ddof: int = 1) -> float:
    """
    Calculate sample variance with degrees of freedom adjustment.

    Formula: s² = (1/(n-ddof)) * Σᵢ (xᵢ - x̄)²

    Args:
        values: 1D array of numeric values.
        ddof: Delta degrees of freedom. Default 1 (Bessel's correction).

    Returns:
        Sample variance.

    Note:
        ddof=1 gives unbiased estimate of population variance.
        ddof=0 gives biased (maximum likelihood) estimate.
    """
    # TODO: Implement in Week 4
    raise NotImplementedError("Implement this function in Week 4")


def calculate_std(values: np.ndarray, ddof: int = 1) -> float:
    """
    Calculate sample standard deviation.

    Formula: s = √(variance)

    Args:
        values: 1D array of numeric values.
        ddof: Delta degrees of freedom.

    Returns:
        Sample standard deviation.
    """
    # TODO: Implement in Week 4
    raise NotImplementedError("Implement this function in Week 4")


def calculate_skewness(values: np.ndarray) -> float:
    """
    Calculate Fisher-Pearson coefficient of skewness.

    Formula: γ₁ = m₃ / m₂^(3/2)
    where mₖ = (1/n) * Σᵢ (xᵢ - x̄)^k

    Interpretation:
        - skewness > 0: Right-tailed (e.g., income distributions)
        - skewness < 0: Left-tailed (e.g., exam scores near maximum)
        - skewness ≈ 0: Symmetric (e.g., normal distribution)

    For yield data:
        Yields are typically left-skewed (most seasons near the
        agronomic ceiling, occasional drought years far below it).

    Args:
        values: 1D array of numeric values.

    Returns:
        Skewness coefficient.
    """
    # TODO: Implement in Week 4
    raise NotImplementedError("Implement this function in Week 4")


def calculate_kurtosis(values: np.ndarray) -> float:
    """
    Calculate excess kurtosis.

    Formula: κ = m₄ / m₂² - 3

    The -3 gives "excess" kurtosis (normal distribution has κ = 0).

    Interpretation:
        - κ > 0: Heavy tails (more outliers than normal)
        - κ < 0: Light tails (fewer outliers than normal)
        - κ ≈ 0: Similar to normal distribution

    Args:
        values: 1D array of numeric values.

    Returns:
        Excess kurtosis.
    """
    # TODO: Implement in Week 4
    raise NotImplementedError("Implement this function in Week 4")


def five_number_summary(values: np.ndarray) -> Tuple[float, float, float, float, float]:
    """
    Calculate five-number summary.

    Returns: (min, Q1, median, Q3, max)

    Args:
        values: 1D array of numeric values.

    Returns:
        Tuple of (min, Q1, median, Q3, max).
    """
    # TODO: Implement in Week 4
    raise NotImplementedError("Implement this function in Week 4")
