"""
Linear regression implemented from scratch.

This module provides OLS regression without using sklearn.

Mathematical Background:
------------------------
OLS Closed-Form Solution:
    β̂ = (XᵀX)⁻¹Xᵀy

Gradient Descent Update:
    β_t+1 = β_t - α * ∇L
    where ∇L = (2/n) * Xᵀ(Xβ - y)

MSE Loss:
    L = (1/n) * Σᵢ (yᵢ - ŷᵢ)²
"""

from typing import Optional

import numpy as np


class LinearRegression:
    """
    Ordinary Least Squares Linear Regression.

    Supports two fitting methods:
        1. Closed-form (normal equations) - O(p³) where p = features
        2. Gradient descent - O(n * p * iterations)

    For yield data:
        Can predict continuous outcomes like yield (bu/acre)
        given weather and county characteristics.

    Attributes:
        coefficients_: Model coefficients (weights).
        intercept_: Model intercept (bias).
        method: Fitting method ('closed_form' or 'gradient_descent').

    Example:
        >>> model = LinearRegression(method='gradient_descent')
        >>> model.fit(X_train, y_train, learning_rate=0.01)
        >>> predictions = model.predict(X_test)
    """

    def __init__(self, method: str = "closed_form") -> None:
        """
        Initialize LinearRegression.

        Args:
            method: 'closed_form' or 'gradient_descent'.
        """
        self.method = method
        self.coefficients_: Optional[np.ndarray] = None
        self.intercept_: Optional[float] = None

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        learning_rate: float = 0.01,
        n_iterations: int = 1000,
        verbose: bool = False,
    ) -> "LinearRegression":
        """
        Fit the linear regression model.

        Args:
            X: Feature matrix of shape (n_samples, n_features).
            y: Target vector of shape (n_samples,).
            learning_rate: Learning rate for gradient descent.
            n_iterations: Number of iterations for gradient descent.
            verbose: Print loss during training.

        Returns:
            self: The fitted model.
        """
        if self.method == "closed_form":
            return self._fit_closed_form(X, y)
        else:
            return self._fit_gradient_descent(X, y, learning_rate, n_iterations, verbose)

    def _fit_closed_form(self, X: np.ndarray, y: np.ndarray) -> "LinearRegression":
        """
        Fit using normal equations.

        Mathematical derivation:
            Minimize ||y - Xβ||²
            ∂L/∂β = 0
            ⟹ X'Xβ = X'y
            ⟹ β = (X'X)⁻¹X'y

        Args:
            X: Feature matrix.
            y: Target vector.

        Returns:
            self: The fitted model.
        """
        # TODO: Implement in Week 9
        # Add column of ones for intercept
        # Compute (X'X)^(-1) X'y
        raise NotImplementedError("Implement this method in Week 9")

    def _fit_gradient_descent(
        self,
        X: np.ndarray,
        y: np.ndarray,
        learning_rate: float,
        n_iterations: int,
        verbose: bool,
    ) -> "LinearRegression":
        """
        Fit using batch gradient descent.

        Why use this over closed-form?
            - Scales better to large n (decades of county-level records)
            - Extends naturally to regularized versions
            - Prepares intuition for neural network training

        Update rule:
            β = β - α * (2/n) * X'(Xβ - y)

        Args:
            X: Feature matrix.
            y: Target vector.
            learning_rate: Step size.
            n_iterations: Number of updates.
            verbose: Print progress.

        Returns:
            self: The fitted model.
        """
        # TODO: Implement in Week 9
        raise NotImplementedError("Implement this method in Week 9")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the fitted model.

        Args:
            X: Feature matrix of shape (n_samples, n_features).

        Returns:
            Predictions of shape (n_samples,).

        Raises:
            RuntimeError: If model is not fitted.
        """
        # TODO: Implement in Week 9
        raise NotImplementedError("Implement this method in Week 9")

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate R² score.

        Formula: R² = 1 - SS_res / SS_tot
        where SS_res = Σ(y - ŷ)², SS_tot = Σ(y - ȳ)²

        Args:
            X: Feature matrix.
            y: True values.

        Returns:
            R² score.
        """
        # TODO: Implement in Week 9
        raise NotImplementedError("Implement this method in Week 9")
