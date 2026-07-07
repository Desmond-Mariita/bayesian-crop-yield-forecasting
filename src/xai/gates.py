"""Evidence and convergence gates — models activate on data, not dates (LINV-003).

Mirrors the keragita-farm-intelligence gate pattern (ADR-008): before any inference, a
pure gate evaluator checks whether enough evidence exists; below the gate the model emits
a ``RejectionCard`` rather than a near-prior posterior dressed up as output. The
convergence thresholds are the production ones: R-hat < 1.01, bulk/tail ESS > 400, zero
divergences.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

from src.xai.cards import RejectionCard, RejectionCode

# Production convergence thresholds (keragita-farm-intelligence ADR-008, Decision 5).
R_HAT_MAX: float = 1.01
ESS_BULK_MIN: float = 400.0
ESS_TAIL_MIN: float = 400.0
DIVERGENCES_MAX: int = 0

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GateStatus:
    """Outcome of a gate evaluation.

    Attributes:
        met: Whether every requirement is satisfied.
        current: Observed value per requirement key.
        required: Required threshold per requirement key.
        missing: Requirement keys that are not satisfied, in declaration order.
    """

    met: bool
    # hash=False on the proxy mappings keeps the frozen status hashable (see cards.py).
    current: Mapping[str, int | float] = field(hash=False)
    required: Mapping[str, int | float] = field(hash=False)
    missing: Tuple[str, ...]

    def __post_init__(self) -> None:
        """Deep-freeze the mappings so immutability is not merely shallow."""
        object.__setattr__(self, "current", MappingProxyType(dict(self.current)))
        object.__setattr__(self, "required", MappingProxyType(dict(self.required)))


@dataclass(frozen=True)
class EvidenceGate:
    """Minimum-evidence thresholds a model must meet before inference is allowed.

    Attributes:
        requirements: Mapping of requirement key to the minimum value that must be
            observed (e.g. ``{"n_complete_seasons": 3}``).
    """

    requirements: Mapping[str, float]

    def evaluate(self, current: Mapping[str, float]) -> GateStatus:
        """Evaluate the gate against observed evidence counts.

        Args:
            current: Observed value per requirement key; absent keys count as 0.

        Returns:
            The gate status, with unmet requirement keys listed in ``missing``.
        """
        absent = tuple(key for key in self.requirements if key not in current)
        if absent:
            # Fail-closed but loud: an absent key counts as zero evidence, which is the
            # safe direction — but if it is a typo in the caller's key names, silence
            # would mask an integration bug (the model just never activates).
            logger.warning("evidence gate: no observation for %s — counting as 0", absent)
        observed = {key: float(current.get(key, 0.0)) for key in self.requirements}
        missing = tuple(
            key for key, required in self.requirements.items() if observed[key] < float(required)
        )
        met = not missing
        logger.debug("evidence gate evaluated: met=%s missing=%s", met, missing)
        return GateStatus(
            met=met, current=observed, required=dict(self.requirements), missing=missing
        )

    def reject_if_unmet(
        self, current: Mapping[str, float], data_source: str
    ) -> Optional[RejectionCard]:
        """Evaluate the gate and build the below-gate rejection when it is unmet.

        Args:
            current: Observed value per requirement key; absent keys count as 0.
            data_source: Data-source tag to stamp on the rejection card.

        Returns:
            None when the gate is met; otherwise a ``RejectionCard`` with code
            ``MISSING_DATA`` describing every unmet requirement.
        """
        status = self.evaluate(current)
        if status.met:
            return None
        conditions = "; ".join(
            f"{key} >= {status.required[key]:g} (current {status.current[key]:g})"
            for key in status.missing
        )
        return RejectionCard(
            rejection_code=RejectionCode.MISSING_DATA,
            recommendation=f"Gate condition: {conditions}",
            data_source=data_source,
            missing_requirements=status.missing,
        )


def evaluate_convergence(
    r_hat: float, ess_bulk: float, ess_tail: float, divergences: int
) -> GateStatus:
    """Check MCMC convergence diagnostics against the production thresholds.

    A model whose sampling run fails any of these checks may not ship its posterior;
    the correct output is a ``RejectionCard`` with code ``NOT_CONVERGED``.

    Args:
        r_hat: Largest potential-scale-reduction statistic across parameters.
        ess_bulk: Smallest bulk effective sample size across parameters.
        ess_tail: Smallest tail effective sample size across parameters.
        divergences: Number of divergent transitions after tuning.

    Returns:
        The gate status; ``missing`` names each failed diagnostic.
    """
    current = {
        "r_hat": float(r_hat),
        "ess_bulk": float(ess_bulk),
        "ess_tail": float(ess_tail),
        "divergences": int(divergences),
    }
    required = {
        "r_hat": R_HAT_MAX,
        "ess_bulk": ESS_BULK_MIN,
        "ess_tail": ESS_TAIL_MIN,
        "divergences": DIVERGENCES_MAX,
    }
    # Strict boundaries, matching the documented criteria exactly (ADR-008 / LINV-003):
    # pass requires r_hat < 1.01, ess > 400, divergences == 0 — boundary values FAIL.
    failed = []
    if current["r_hat"] >= R_HAT_MAX:
        failed.append("r_hat")
    if current["ess_bulk"] <= ESS_BULK_MIN:
        failed.append("ess_bulk")
    if current["ess_tail"] <= ESS_TAIL_MIN:
        failed.append("ess_tail")
    if current["divergences"] > DIVERGENCES_MAX:
        failed.append("divergences")
    met = not failed
    logger.debug("convergence gate evaluated: met=%s failed=%s", met, failed)
    return GateStatus(met=met, current=current, required=required, missing=tuple(failed))
