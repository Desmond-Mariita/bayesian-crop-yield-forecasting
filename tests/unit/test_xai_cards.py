"""Unit tests for the XAI card contract (src/xai/cards.py)."""

import dataclasses

import pytest

from src.xai.cards import DataQuality, ExplanationCard, RejectionCard, RejectionCode


def _explanation_kwargs() -> dict:
    """Return a valid keyword set for building an ExplanationCard.

    Returns:
        Keyword arguments accepted by ``ExplanationCard``.
    """
    return {
        "plain_summary": "Expected maize yield is 2.1 t/ha (90% interval 1.4-2.8).",
        "confidence": 0.82,
        "data_quality": DataQuality.COMPLETE,
        "model_version": "yield-hier-0.1.0",
        "feature_pipeline_version": "features-0.1.0",
        "data_source": "api_nass",
    }


class TestExplanationCard:
    """Construction and validation of ExplanationCard."""

    def test_valid_card_constructs(self) -> None:
        """A fully-specified card constructs and keeps its fields."""
        card = ExplanationCard(**_explanation_kwargs())
        assert card.confidence == 0.82
        assert card.data_quality is DataQuality.COMPLETE
        assert card.technical_detail == {}

    def test_card_is_immutable(self) -> None:
        """Cards are frozen; assignment raises."""
        card = ExplanationCard(**_explanation_kwargs())
        with pytest.raises(dataclasses.FrozenInstanceError):
            card.confidence = 0.5  # type: ignore[misc]

    @pytest.mark.parametrize("confidence", [-0.01, 1.01, 2.0])
    def test_out_of_range_confidence_rejected(self, confidence: float) -> None:
        """Confidence outside [0, 1] raises ValueError."""
        kwargs = _explanation_kwargs() | {"confidence": confidence}
        with pytest.raises(ValueError, match="confidence"):
            ExplanationCard(**kwargs)

    @pytest.mark.parametrize(
        "field_name",
        ["plain_summary", "model_version", "feature_pipeline_version", "data_source"],
    )
    def test_empty_required_field_rejected(self, field_name: str) -> None:
        """Empty summary or provenance fields raise ValueError (LINV-001)."""
        kwargs = _explanation_kwargs() | {field_name: "  "}
        with pytest.raises(ValueError, match=field_name):
            ExplanationCard(**kwargs)

    def test_technical_detail_carries_payload(self) -> None:
        """The technical payload is stored as given."""
        detail = {"posterior_mean": 2.1, "r_hat": 1.002}
        card = ExplanationCard(**_explanation_kwargs(), technical_detail=detail)
        assert card.technical_detail["r_hat"] == 1.002

    def test_technical_detail_is_deeply_immutable(self) -> None:
        """The payload is snapshotted and proxied: neither the card's mapping nor the
        caller's original dict can change what the card reports."""
        detail = {"posterior_mean": 2.1}
        card = ExplanationCard(**_explanation_kwargs(), technical_detail=detail)
        with pytest.raises(TypeError):
            card.technical_detail["posterior_mean"] = 999.0  # type: ignore[index]
        detail["posterior_mean"] = 999.0  # mutating the source dict must not leak in
        assert card.technical_detail["posterior_mean"] == 2.1


class TestRejectionCard:
    """Construction and validation of RejectionCard."""

    def test_valid_rejection_constructs(self) -> None:
        """A rejection card constructs with defaults."""
        card = RejectionCard(
            rejection_code=RejectionCode.MISSING_DATA,
            recommendation="Record at least 3 complete crop seasons.",
            data_source="manual_app",
            missing_requirements=("n_complete_seasons",),
        )
        assert card.confidence == 0.0
        assert card.rejection_code is RejectionCode.MISSING_DATA
        assert card.missing_requirements == ("n_complete_seasons",)

    def test_empty_recommendation_rejected(self) -> None:
        """A rejection without a recommendation is invalid."""
        with pytest.raises(ValueError, match="recommendation"):
            RejectionCard(
                rejection_code=RejectionCode.LOW_CONFIDENCE,
                recommendation="",
                data_source="manual_app",
            )

    def test_empty_data_source_rejected(self) -> None:
        """Every card must carry a data-source tag."""
        with pytest.raises(ValueError, match="data_source"):
            RejectionCard(
                rejection_code=RejectionCode.NOT_CONVERGED,
                recommendation="Increase tuning steps and re-run sampling.",
                data_source="",
            )

    def test_rejection_codes_enumerate_reasons(self) -> None:
        """The three withholding reasons are all representable."""
        codes = {code.value for code in RejectionCode}
        assert codes == {"MISSING_DATA", "LOW_CONFIDENCE", "NOT_CONVERGED"}
