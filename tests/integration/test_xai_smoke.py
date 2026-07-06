"""Integration smoke test: a minimal model honouring the full XAI contract end-to-end."""

from typing import Union

import numpy as np

from src.xai import (
    DataQuality,
    EvidenceGate,
    ExplainableModel,
    ExplanationCard,
    RejectionCard,
    RejectionCode,
)

SEED = 42
MIN_SEASONS = 3


class MeanYieldModel(ExplainableModel):
    """Toy yield model: predicts the historical mean, gated on season count.

    This is deliberately trivial — the test exercises the *contract* (gate check first,
    card always returned, never an exception), not the estimator.
    """

    def __init__(self, seasons: np.ndarray) -> None:
        """Store the historical seasons available as evidence.

        Args:
            seasons: 1D array of per-season yield observations.
        """
        self._seasons = seasons
        self._gate = EvidenceGate(requirements={"n_complete_seasons": MIN_SEASONS})

    def explain_or_reject(self, X: np.ndarray) -> Union[ExplanationCard, RejectionCard]:
        """Predict mean yield or reject when below the evidence gate.

        Args:
            X: Feature matrix (unused by this toy estimator).

        Returns:
            An ``ExplanationCard`` above the gate, a ``RejectionCard`` below it.
        """
        rejection = self._gate.reject_if_unmet(
            {"n_complete_seasons": float(self._seasons.size)}, data_source="manual_app"
        )
        if rejection is not None:
            return rejection
        mean_yield = float(np.mean(self._seasons))
        return ExplanationCard(
            plain_summary=f"Expected yield is {mean_yield:.2f} t/ha (historical mean).",
            confidence=0.5,
            data_quality=DataQuality.COMPLETE,
            model_version="mean-yield-0.1.0",
            feature_pipeline_version="identity-0.1.0",
            data_source="manual_app",
            technical_detail={"n_seasons": int(self._seasons.size), "seed": SEED},
        )


def test_below_gate_yields_structured_rejection() -> None:
    """With too few seasons the model refuses with MISSING_DATA — it does not raise."""
    rng = np.random.default_rng(SEED)
    model = MeanYieldModel(seasons=rng.normal(2.0, 0.3, size=MIN_SEASONS - 1))
    card = model.explain_or_reject(np.empty((0, 0)))
    assert isinstance(card, RejectionCard)
    assert card.rejection_code is RejectionCode.MISSING_DATA
    assert card.missing_requirements == ("n_complete_seasons",)


def test_above_gate_yields_explanation_with_provenance() -> None:
    """With enough seasons the model explains, carrying versions and data source."""
    rng = np.random.default_rng(SEED)
    model = MeanYieldModel(seasons=rng.normal(2.0, 0.3, size=MIN_SEASONS + 2))
    card = model.explain_or_reject(np.empty((0, 0)))
    assert isinstance(card, ExplanationCard)
    assert card.model_version == "mean-yield-0.1.0"
    assert card.feature_pipeline_version == "identity-0.1.0"
    assert card.data_source == "manual_app"
    assert 0.0 <= card.confidence <= 1.0


def test_same_seed_reproduces_same_card() -> None:
    """Determinism (LINV-008): the same seed produces byte-identical summaries."""
    cards = []
    for _ in range(2):
        rng = np.random.default_rng(SEED)
        model = MeanYieldModel(seasons=rng.normal(2.0, 0.3, size=MIN_SEASONS + 2))
        cards.append(model.explain_or_reject(np.empty((0, 0))))
    assert isinstance(cards[0], ExplanationCard)
    assert cards[0] == cards[1]
