"""
Logistic regression implemented from scratch.

This module provides binary classification without using sklearn.

Mathematical Background:
------------------------
Sigmoid Function:
    σ(z) = 1 / (1 + e^(-z))

Log-Loss (Binary Cross-Entropy):
    L = -(1/n) * Σᵢ [yᵢ log(ŷᵢ) + (1-yᵢ) log(1-ŷᵢ)]

Gradient:
    ∇L = (1/n) * Xᵀ(ŷ - y)
"""

from typing import Optional

import numpy as np


class LogisticRegression:
    """
    Binary Logistic Regression for classification.

    For yield forecasting:
        Predicts the probability of a low-yield event (a season
        falling significantly below the county's historical trend).

    Key insight for Bayesian connection:
        Logistic regression finds point estimates of β. In Phase 2,
        we'll extend this to find the full posterior p(β|data),
        giving us uncertainty in low-yield probabilities.

    Attributes:
        coefficients_: Model weights.
        intercept_: Model bias.
        learning_rate: Step size for gradient descent.
        n_iterations: Number of training iterations.

    Example:
        >>> model = LogisticRegression(learning_rate=0.1)
        >>> model.fit(X_train, y_train)
        >>> probabilities = model.predict_proba(X_test)
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        n_iterations: int = 1000,
    ) -> None:
        """
        Initialize LogisticRegression.

        Args:
            learning_rate: Step size for gradient descent.
            n_iterations: Number of training iterations.
        """
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.coefficients_: Optional[np.ndarray] = None
        self.intercept_: Optional[float] = None
        self.loss_history_: list = []

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        """
        Apply sigmoid function.

        Formula: σ(z) = 1 / (1 + e^(-z))

        Numerically stable implementation to avoid overflow.

        Args:
            z: Linear combination (Xβ + b).

        Returns:
            Probabilities in [0, 1].
        """
        # TODO: Implement in Week 10
        # Hint: Use np.clip to avoid overflow
        raise NotImplementedError("Implement this method in Week 10")

    def _compute_loss(self, y: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Compute binary cross-entropy loss.

        Formula: L = -(1/n) * Σ[y log(ŷ) + (1-y) log(1-ŷ)]

        Args:
            y: True labels.
            y_pred: Predicted probabilities.

        Returns:
            Loss value.
        """
        # TODO: Implement in Week 10
        # Add small epsilon to avoid log(0)
        raise NotImplementedError("Implement this method in Week 10")

    def fit(self, X: np.ndarray, y: np.ndarray, verbose: bool = False) -> "LogisticRegression":
        """
        Fit logistic regression using gradient descent.

        Gradient: ∇L = (1/n) * Xᵀ(ŷ - y)

        Args:
            X: Feature matrix of shape (n_samples, n_features).
            y: Binary labels of shape (n_samples,).
            verbose: Print loss during training.

        Returns:
            self: The fitted model.
        """
        # TODO: Implement in Week 10
        raise NotImplementedError("Implement this method in Week 10")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probability of a low-yield event.

        For yield forecasting:
            This probability feeds directly into risk decisions
            (e.g., crop insurance pricing, reserve planning).

        Args:
            X: Feature matrix.

        Returns:
            Probabilities of shape (n_samples,).
        """
        # TODO: Implement in Week 10
        raise NotImplementedError("Implement this method in Week 10")

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """
        Predict binary labels.

        Args:
            X: Feature matrix.
            threshold: Classification threshold.

        Returns:
            Binary predictions.
        """
        # TODO: Implement in Week 10
        raise NotImplementedError("Implement this method in Week 10")
