"""Explanation and rejection cards — the structured XAI output contract.

Adapted from the keragita-farm-intelligence platform (its INV-001/004/009; here
LINV-001/002 in ``docs/INVARIANTS.md``). An ``ExplanationCard`` communicates a prediction
together with its uncertainty and provenance; a ``RejectionCard`` withholds a prediction
that would not be trustworthy and states why and what is missing. A model must always
return one of the two — never a bare number, never a forced prediction with a warning.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple

CONFIDENCE_MIN: float = 0.0
CONFIDENCE_MAX: float = 1.0


class DataQuality(str, enum.Enum):
    """Input-data completeness classification for a single inference call."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    DEGRADED = "degraded"


class RejectionCode(str, enum.Enum):
    """Machine-readable reason a prediction was withheld."""

    MISSING_DATA = "MISSING_DATA"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    NOT_CONVERGED = "NOT_CONVERGED"


def _require_non_empty(value: str, field_name: str) -> None:
    """Raise if a required string field is empty or whitespace.

    Args:
        value: Field value to check.
        field_name: Name used in the error message.

    Raises:
        ValueError: If ``value`` is empty or whitespace-only.
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_confidence_in_range(confidence: float) -> None:
    """Raise if a confidence value falls outside the closed unit interval.

    Args:
        confidence: Confidence value to check.

    Raises:
        ValueError: If ``confidence`` is not in ``[CONFIDENCE_MIN, CONFIDENCE_MAX]``.
    """
    if not CONFIDENCE_MIN <= confidence <= CONFIDENCE_MAX:
        raise ValueError(
            f"confidence must be in [{CONFIDENCE_MIN}, {CONFIDENCE_MAX}], got {confidence}"
        )


@dataclass(frozen=True)
class ExplanationCard:
    """A prediction explained: plain-language summary, confidence, and provenance.

    Version provenance is mandatory (LINV-001, mirroring production INV-009): an
    explanation that cannot say which model and feature-pipeline versions produced it
    is invalid.

    Attributes:
        plain_summary: One-paragraph, non-technical statement of the prediction.
        confidence: Calibrated confidence in ``[0, 1]``.
        data_quality: Completeness classification of the inputs used.
        model_version: Version of the model that produced the card.
        feature_pipeline_version: Version of the feature pipeline that fed the model.
        data_source: Tag identifying where the input data came from.
        technical_detail: Free-form technical payload (posterior summaries, priors,
            diagnostics) for the expert reader.
    """

    plain_summary: str
    confidence: float
    data_quality: DataQuality
    model_version: str
    feature_pipeline_version: str
    data_source: str
    technical_detail: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate field values at construction time.

        Raises:
            ValueError: If any required field is empty or confidence is out of range.
        """
        _require_non_empty(self.plain_summary, "plain_summary")
        _require_non_empty(self.model_version, "model_version")
        _require_non_empty(self.feature_pipeline_version, "feature_pipeline_version")
        _require_non_empty(self.data_source, "data_source")
        _require_confidence_in_range(self.confidence)


@dataclass(frozen=True)
class RejectionCard:
    """A withheld prediction: structured refusal, not a forced answer (LINV-002).

    Attributes:
        rejection_code: Machine-readable reason for withholding the prediction.
        recommendation: What is needed for the model to produce an answer.
        data_source: Tag identifying where the (insufficient) input data came from.
        missing_requirements: Names of the unmet requirements, when known.
        confidence: Always low; kept as a field so cards render uniformly.
    """

    rejection_code: RejectionCode
    recommendation: str
    data_source: str
    missing_requirements: Tuple[str, ...] = ()
    confidence: float = 0.0

    def __post_init__(self) -> None:
        """Validate field values at construction time.

        Raises:
            ValueError: If any required field is empty or confidence is out of range.
        """
        _require_non_empty(self.recommendation, "recommendation")
        _require_non_empty(self.data_source, "data_source")
        _require_confidence_in_range(self.confidence)
