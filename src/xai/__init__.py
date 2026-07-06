"""Explainable-AI contract: explanation/rejection cards and evidence gates.

Mirrors, in miniature, the XAI contract of the keragita-farm-intelligence production
platform (LINV-001..LINV-003 in ``docs/INVARIANTS.md``): every model returns an
``ExplanationCard`` or a ``RejectionCard`` via ``explain_or_reject`` — never a bare
point estimate, never a forced prediction with a warning.
"""

from src.xai.base import ExplainableModel
from src.xai.cards import DataQuality, ExplanationCard, RejectionCard, RejectionCode
from src.xai.gates import (
    DIVERGENCES_MAX,
    ESS_BULK_MIN,
    ESS_TAIL_MIN,
    R_HAT_MAX,
    EvidenceGate,
    GateStatus,
    evaluate_convergence,
)

__version__ = "0.1.0"

__all__ = [
    "DataQuality",
    "DIVERGENCES_MAX",
    "ESS_BULK_MIN",
    "ESS_TAIL_MIN",
    "EvidenceGate",
    "ExplainableModel",
    "ExplanationCard",
    "GateStatus",
    "R_HAT_MAX",
    "RejectionCard",
    "RejectionCode",
    "evaluate_convergence",
]
