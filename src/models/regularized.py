"""
Regularized regression models implemented from scratch.

This module provides Ridge, Lasso, and Elastic Net without sklearn.

Mathematical Background:
------------------------
Ridge (L2):
    β̂ = (XᵀX + λI)⁻¹Xᵀy
    Shrinks coefficients toward zero.

Lasso (L1):
    min (1/2n)||y - Xβ||² + λ||β||₁
    Can set coefficients exactly to zero (feature selection).
    Requires coordinate descent (no closed-form solution).

Elastic Net:
    min (1/2n)||y - Xβ||² + λ₁||β||₁ + λ₂||β||₂²
"""

from typing import Optional

import numpy as np


class RidgeRegression:
    """
    Ridge regression (L2 regularization).

    Formula: β̂ = (XᵀX + λI)⁻¹Xᵀy

    Properties:
        - Shrinks all coefficients toward zero
        - Never sets coefficients exactly to zero
        - Has closed-form solution
        - Handles multicollinearity well

    Attributes:
        alpha: Regularization strength.
        coefficients_: Fitted weights.
        intercept_: Fitted bias.
    """

    def __init__(self, alpha: float = 1.0) -> None:
        """
        Initialize RidgeRegression.

        Args:
            alpha: Regularization strength. Larger = more regularization.
        """
        self.alpha = alpha
        self.coefficients_: Optional[np.ndarray] = None
        self.intercept_: Optional[float] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RidgeRegression":
        """
        Fit Ridge regression.

        Uses closed-form solution: β = (X'X + αI)⁻¹X'y

        Args:
            X: Feature matrix.
            y: Target vector.

        Returns:
            self: Fitted model.
        """
        # TODO: Implement in Week 11
        raise NotImplementedError("Implement this method in Week 11")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix.

        Returns:
            Predicted target values.
        """
        # TODO: Implement in Week 11
        raise NotImplementedError("Implement this method in Week 11")


class LassoRegression:
    """
    Lasso regression (L1 regularization).

    Objective: min (1/2n)||y - Xβ||² + α||β||₁

    Properties:
        - Can set coefficients exactly to zero
        - Performs feature selection
        - Requires iterative optimization (coordinate descent)

    For yield data:
        Lasso identifies the most important weather and soil features
        for yield prediction by setting irrelevant coefficients to zero.
    """

    def __init__(
        self,
        alpha: float = 1.0,
        max_iter: int = 1000,
        tol: float = 1e-4,
    ) -> None:
        """
        Initialize LassoRegression.

        Args:
            alpha: Regularization strength.
            max_iter: Maximum iterations for coordinate descent.
            tol: Convergence tolerance.
        """
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.coefficients_: Optional[np.ndarray] = None
        self.intercept_: Optional[float] = None

    def _soft_threshold(self, x: float, threshold: float) -> float:
        """
        Soft thresholding operator for L1 penalty.

        Formula:
            S(x, λ) = sign(x) * max(|x| - λ, 0)

        This is the proximal operator for L1 norm.

        Args:
            x: Input value.
            threshold: Threshold (lambda).

        Returns:
            Soft-thresholded value.
        """
        # TODO: Implement in Week 11
        raise NotImplementedError("Implement this method in Week 11")

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LassoRegression":
        """
        Fit Lasso using coordinate descent.

        Why coordinate descent?
            L1 penalty is not differentiable at zero.
            We optimize one coordinate at a time using
            the soft-thresholding operator.

        Args:
            X: Feature matrix.
            y: Target vector.

        Returns:
            self: Fitted model.
        """
        # TODO: Implement in Week 11
        raise NotImplementedError("Implement this method in Week 11")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Feature matrix.

        Returns:
            Predicted target values.
        """
        # TODO: Implement in Week 11
        raise NotImplementedError("Implement this method in Week 11")
