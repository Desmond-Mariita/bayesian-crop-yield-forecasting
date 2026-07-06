"""Unit tests for evidence and convergence gates (src/xai/gates.py)."""

import pytest

from src.xai.cards import RejectionCard, RejectionCode
from src.xai.gates import (
    DIVERGENCES_MAX,
    ESS_BULK_MIN,
    ESS_TAIL_MIN,
    R_HAT_MAX,
    EvidenceGate,
    evaluate_convergence,
)

YIELD_GATE = EvidenceGate(requirements={"n_complete_seasons": 3, "n_counties": 10})


class TestEvidenceGate:
    """Evaluation semantics of EvidenceGate."""

    def test_gate_met_when_all_requirements_satisfied(self) -> None:
        """Meeting every threshold yields met=True and no missing keys."""
        status = YIELD_GATE.evaluate({"n_complete_seasons": 5, "n_counties": 12})
        assert status.met
        assert status.missing == ()

    def test_gate_unmet_lists_missing_requirements(self) -> None:
        """Unmet thresholds are listed by key, in declaration order."""
        status = YIELD_GATE.evaluate({"n_complete_seasons": 2, "n_counties": 12})
        assert not status.met
        assert status.missing == ("n_complete_seasons",)
        assert status.current["n_complete_seasons"] == 2.0

    def test_absent_evidence_counts_as_zero(self) -> None:
        """Keys absent from the observed mapping count as zero evidence."""
        status = YIELD_GATE.evaluate({})
        assert not status.met
        assert status.missing == ("n_complete_seasons", "n_counties")
        assert status.current == {"n_complete_seasons": 0.0, "n_counties": 0.0}

    def test_boundary_value_meets_gate(self) -> None:
        """Evidence exactly at the threshold meets the gate (>= semantics)."""
        status = YIELD_GATE.evaluate({"n_complete_seasons": 3, "n_counties": 10})
        assert status.met

    def test_reject_if_unmet_returns_none_when_met(self) -> None:
        """No rejection card is produced when the gate is met."""
        card = YIELD_GATE.reject_if_unmet(
            {"n_complete_seasons": 4, "n_counties": 11}, data_source="api_nass"
        )
        assert card is None

    def test_reject_if_unmet_builds_missing_data_card(self) -> None:
        """Below the gate, a MISSING_DATA rejection names every unmet requirement."""
        card = YIELD_GATE.reject_if_unmet({"n_counties": 11}, data_source="api_nass")
        assert isinstance(card, RejectionCard)
        assert card.rejection_code is RejectionCode.MISSING_DATA
        assert card.missing_requirements == ("n_complete_seasons",)
        assert "n_complete_seasons >= 3" in card.recommendation
        assert card.data_source == "api_nass"


class TestConvergenceGate:
    """Convergence diagnostics against the production thresholds."""

    def test_clean_run_passes(self) -> None:
        """Diagnostics within every threshold meet the gate."""
        status = evaluate_convergence(r_hat=1.001, ess_bulk=900.0, ess_tail=850.0, divergences=0)
        assert status.met
        assert status.missing == ()

    @pytest.mark.parametrize(
        ("kwargs", "expected_failure"),
        [
            ({"r_hat": 1.02, "ess_bulk": 900.0, "ess_tail": 850.0, "divergences": 0}, "r_hat"),
            ({"r_hat": 1.001, "ess_bulk": 100.0, "ess_tail": 850.0, "divergences": 0}, "ess_bulk"),
            ({"r_hat": 1.001, "ess_bulk": 900.0, "ess_tail": 50.0, "divergences": 0}, "ess_tail"),
            (
                {"r_hat": 1.001, "ess_bulk": 900.0, "ess_tail": 850.0, "divergences": 3},
                "divergences",
            ),
        ],
    )
    def test_each_diagnostic_failure_is_named(self, kwargs: dict, expected_failure: str) -> None:
        """Each failing diagnostic appears by name in missing."""
        status = evaluate_convergence(**kwargs)
        assert not status.met
        assert expected_failure in status.missing

    def test_thresholds_match_production_values(self) -> None:
        """The module constants pin the ADR-008 thresholds."""
        assert R_HAT_MAX == 1.01
        assert ESS_BULK_MIN == 400.0
        assert ESS_TAIL_MIN == 400.0
        assert DIVERGENCES_MAX == 0
