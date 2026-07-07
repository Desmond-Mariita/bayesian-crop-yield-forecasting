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

    def test_absent_evidence_warns_loudly(self, caplog: pytest.LogCaptureFixture) -> None:
        """Fail-closed but loud: absent keys are logged so key typos cannot hide."""
        with caplog.at_level("WARNING", logger="src.xai.gates"):
            YIELD_GATE.evaluate({"n_complete_seasons": 5})
        assert "n_counties" in caplog.text
        caplog.clear()
        with caplog.at_level("WARNING", logger="src.xai.gates"):
            YIELD_GATE.evaluate({"n_complete_seasons": 5, "n_counties": 12})
        assert caplog.text == ""

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

    def test_boundary_values_fail_strictly(self) -> None:
        """Documented criteria are strict: exactly 1.01 / exactly 400 must FAIL.

        Pass requires r_hat < 1.01 and ess > 400 — not <= / >=. This pins the boundary
        semantics the external review panel flagged.
        """
        status = evaluate_convergence(r_hat=1.01, ess_bulk=400.0, ess_tail=400.0, divergences=0)
        assert not status.met
        assert status.missing == ("r_hat", "ess_bulk", "ess_tail")

    def test_divergences_kept_as_int(self) -> None:
        """The divergence count stays an integer in the reported status."""
        status = evaluate_convergence(r_hat=1.001, ess_bulk=900.0, ess_tail=850.0, divergences=2)
        assert status.current["divergences"] == 2
        assert isinstance(status.current["divergences"], int)

    def test_status_mappings_are_deeply_immutable(self) -> None:
        """GateStatus mappings cannot be mutated after construction."""
        status = evaluate_convergence(r_hat=1.001, ess_bulk=900.0, ess_tail=850.0, divergences=0)
        with pytest.raises(TypeError):
            status.current["r_hat"] = 0.5  # type: ignore[index]
        with pytest.raises(TypeError):
            status.required["r_hat"] = 9.9  # type: ignore[index]
