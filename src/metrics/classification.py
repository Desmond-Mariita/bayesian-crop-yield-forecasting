"""
Classification metrics implemented from scratch.

This module provides evaluation metrics without using sklearn.
"""

from typing import Tuple

import numpy as np


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Calculate confusion matrix.

    Returns 2x2 matrix:
        [[TN, FP],
         [FN, TP]]

    Args:
        y_true: True binary labels.
        y_pred: Predicted binary labels.

    Returns:
        Confusion matrix as numpy array.
    """
    # TODO: Implement in Week 10
    raise NotImplementedError("Implement this function in Week 10")


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate accuracy.

    Formula: (TP + TN) / (TP + TN + FP + FN)

    Args:
        y_true: True labels.
        y_pred: Predicted labels.

    Returns:
        Accuracy score.
    """
    # TODO: Implement in Week 10
    raise NotImplementedError("Implement this function in Week 10")


def precision(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate precision.

    Formula: TP / (TP + FP)

    "Of all predicted positives, how many were correct?"

    Args:
        y_true: True labels.
        y_pred: Predicted labels.

    Returns:
        Precision score.
    """
    # TODO: Implement in Week 10
    raise NotImplementedError("Implement this function in Week 10")


def recall(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate recall (sensitivity, true positive rate).

    Formula: TP / (TP + FN)

    "Of all actual positives, how many did we catch?"

    For yield forecasting:
        High recall means catching most low-yield seasons,
        but may raise too many false alarms in normal years.

    Args:
        y_true: True labels.
        y_pred: Predicted labels.

    Returns:
        Recall score.
    """
    # TODO: Implement in Week 10
    raise NotImplementedError("Implement this function in Week 10")


def f1_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate F1 score.

    Formula: F1 = 2 * (precision * recall) / (precision + recall)

    Harmonic mean of precision and recall.

    Args:
        y_true: True labels.
        y_pred: Predicted labels.

    Returns:
        F1 score.
    """
    # TODO: Implement in Week 10
    raise NotImplementedError("Implement this function in Week 10")


def roc_curve(
    y_true: np.ndarray,
    y_scores: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate ROC curve.

    Args:
        y_true: True binary labels.
        y_scores: Predicted probabilities or scores.

    Returns:
        Tuple of (fpr, tpr, thresholds).
    """
    # TODO: Implement in Week 10
    raise NotImplementedError("Implement this function in Week 10")


def auc(fpr: np.ndarray, tpr: np.ndarray) -> float:
    """
    Calculate Area Under the ROC Curve using trapezoidal rule.

    Formula: AUC = Σᵢ (fprᵢ₊₁ - fprᵢ) * (tprᵢ₊₁ + tprᵢ) / 2

    Args:
        fpr: False positive rates.
        tpr: True positive rates.

    Returns:
        AUC value.
    """
    # TODO: Implement in Week 10
    raise NotImplementedError("Implement this function in Week 10")
