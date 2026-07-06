"""
Regression metrics implemented from scratch.

This module provides evaluation metrics without using sklearn.
"""

import numpy as np


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Squared Error.

    Formula: MSE = (1/n) * Σᵢ (yᵢ - ŷᵢ)²

    Args:
        y_true: True values.
        y_pred: Predicted values.

    Returns:
        MSE value.
    """
    # TODO: Implement in Week 9
    raise NotImplementedError("Implement this function in Week 9")


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Root Mean Squared Error.

    Formula: RMSE = √MSE

    Args:
        y_true: True values.
        y_pred: Predicted values.

    Returns:
        RMSE value.
    """
    # TODO: Implement in Week 9
    raise NotImplementedError("Implement this function in Week 9")


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error.

    Formula: MAE = (1/n) * Σᵢ |yᵢ - ŷᵢ|

    Args:
        y_true: True values.
        y_pred: Predicted values.

    Returns:
        MAE value.
    """
    # TODO: Implement in Week 9
    raise NotImplementedError("Implement this function in Week 9")


def r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate R² (coefficient of determination).

    Formula: R² = 1 - SS_res / SS_tot
    where SS_res = Σ(y - ŷ)², SS_tot = Σ(y - ȳ)²

    Interpretation:
        - R² = 1: Perfect fit
        - R² = 0: Model predicts the mean
        - R² < 0: Model worse than predicting mean

    Args:
        y_true: True values.
        y_pred: Predicted values.

    Returns:
        R² score.
    """
    # TODO: Implement in Week 9
    raise NotImplementedError("Implement this function in Week 9")


def adjusted_r_squared(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_features: int,
) -> float:
    """
    Calculate Adjusted R².

    Formula: Adj R² = 1 - (1 - R²) * (n - 1) / (n - p - 1)

    Adjusts for number of predictors to avoid overfitting illusion.

    Args:
        y_true: True values.
        y_pred: Predicted values.
        n_features: Number of features in the model.

    Returns:
        Adjusted R² score.
    """
    # TODO: Implement in Week 9
    raise NotImplementedError("Implement this function in Week 9")
