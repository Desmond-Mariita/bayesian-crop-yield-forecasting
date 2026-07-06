"""Abstract base class making the XAI contract mandatory for every model (LINV-001)."""

from __future__ import annotations

import abc
from typing import Union

import numpy as np

from src.xai.cards import ExplanationCard, RejectionCard


class ExplainableModel(abc.ABC):
    """Base class for models bound by the card contract.

    Subclasses implement ``explain_or_reject`` as their only public inference entry
    point: it must return a structured card and must not raise on low-quality input —
    withholding a prediction is expressed as a ``RejectionCard``, not an exception.
    """

    @abc.abstractmethod
    def explain_or_reject(self, X: np.ndarray) -> Union[ExplanationCard, RejectionCard]:
        """Run inference and return a structured explanation or a structured refusal.

        Args:
            X: Feature matrix for the inference call.

        Returns:
            An ``ExplanationCard`` for a trustworthy prediction, or a ``RejectionCard``
            when the prediction must be withheld (below evidence gate, low confidence,
            or non-converged sampling).
        """
