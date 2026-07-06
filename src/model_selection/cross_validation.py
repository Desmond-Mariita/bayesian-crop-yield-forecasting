"""
Cross-validation utilities implemented from scratch.

This directly addresses the BSc weakness in "Design & Analysis of Experiments".
"""

from typing import Any, Generator, List, Optional, Tuple

import numpy as np


def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: Optional[int] = None,
    shuffle: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data into train and test sets.

    Args:
        X: Feature matrix.
        y: Target vector.
        test_size: Proportion of data for testing.
        random_state: Seed for reproducibility.
        shuffle: Whether to shuffle before splitting.

    Returns:
        Tuple of (X_train, X_test, y_train, y_test).
    """
    # TODO: Implement in Week 11
    raise NotImplementedError("Implement this function in Week 11")


def k_fold_split(
    n_samples: int,
    n_folds: int = 5,
    shuffle: bool = True,
    random_state: Optional[int] = None,
) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
    """
    Generate K-Fold cross-validation indices.

    Args:
        n_samples: Total number of samples.
        n_folds: Number of folds.
        shuffle: Whether to shuffle indices.
        random_state: Seed for reproducibility.

    Yields:
        Tuple of (train_indices, val_indices) for each fold.
    """
    # TODO: Implement in Week 11
    raise NotImplementedError("Implement this function in Week 11")


def cross_val_score(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    n_folds: int = 5,
    scoring: str = "accuracy",
) -> List[float]:
    """
    Evaluate model using cross-validation.

    Args:
        model: Model with fit() and predict() methods.
        X: Feature matrix.
        y: Target vector.
        n_folds: Number of CV folds.
        scoring: Metric to use ('accuracy', 'f1', 'r2').

    Returns:
        List of scores for each fold.
    """
    # TODO: Implement in Week 11
    raise NotImplementedError("Implement this function in Week 11")
