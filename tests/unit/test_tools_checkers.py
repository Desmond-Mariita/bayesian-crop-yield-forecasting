"""Unit tests for the pure functions of the CI gate tools (tools/*.py).

Closes guidelines self-audit deviation 2: the checkers were previously smoke-covered
only by running inside verify.py/CI. These tests pin the parsing/matching behaviour
directly. The tools directory is not a package, so it is imported via sys.path.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("tools").resolve()))

import check_data_cards  # noqa: E402
import check_notebooks  # noqa: E402


class TestParseFrontmatter:
    """check_data_cards.parse_frontmatter — the restricted frontmatter syntax."""

    def test_scalars_lists_and_comments(self) -> None:
        """Scalars, block lists, whitespace-comments, and quotes all behave."""
        text = (
            "---\n"
            "dataset_id: DC-x  # inline comment\n"
            "source_url: https://example.com/page#fragment\n"
            "known_limitations:\n"
            "  - first  # noted\n"
            '  - "second"\n'
            "---\n"
            "body\n"
        )
        fields = check_data_cards.parse_frontmatter(text)
        assert fields["dataset_id"] == "DC-x"
        assert fields["source_url"] == "https://example.com/page#fragment"
        assert fields["known_limitations"] == ["first", "second"]

    @pytest.mark.parametrize(
        ("text", "match"),
        [
            ("dataset_id: DC-x\n---\n", "must start"),
            ("---\ndataset_id: DC-x\n", "never closed"),
            ("---\n- orphan item\n---\n", "outside a list"),
            ('---\nknown_limitations:\n  - ""\n---\n', "empty list item"),
            ("---\nknown_limitations:\n  - # comment only\n---\n", "empty list item"),
            ("---\njust some words\n---\n", "expected 'key: value'"),
        ],
    )
    def test_malformed_frontmatter_raises(self, text: str, match: str) -> None:
        """Every malformed shape fails loudly with a located error."""
        with pytest.raises(ValueError, match=match):
            check_data_cards.parse_frontmatter(text)


class TestValidateCard:
    """check_data_cards.validate_card — schema enforcement on real files."""

    def test_valid_repo_cards_pass(self) -> None:
        """The repo's own cards are the golden fixtures."""
        for card in sorted(Path("docs/data_cards").glob("DC-*.md")):
            assert check_data_cards.validate_card(card) == []

    def test_missing_fields_and_bad_status_reported(self, tmp_path: Path) -> None:
        """Missing required fields and an unknown status each produce a violation."""
        card = tmp_path / "DC-bad.md"
        card.write_text("---\ndataset_id: DC-bad\nstatus: shiny\n---\n", encoding="utf-8")
        violations = check_data_cards.validate_card(card)
        assert any("dataset_name" in v for v in violations)
        assert any("status must be one of" in v for v in violations)
        assert any("known_limitations" in v for v in violations)


class TestGraduationGateHelpers:
    """check_notebooks — ledger loading, path mirroring, dedicated-test matching."""

    def test_load_ledger_returns_the_real_ledger(self) -> None:
        """The ledger imports and contains the first graduated name."""
        ledger = check_notebooks.load_ledger()
        assert isinstance(ledger, frozenset)
        assert "src.data.acquisition:download_nass_yields" in ledger

    def test_expected_notebook_mirrors_module_path(self) -> None:
        """src.statistics.descriptive → notebooks/statistics/descriptive.ipynb."""
        notebook = check_notebooks.expected_notebook("src.statistics.descriptive")
        assert notebook == Path("notebooks/statistics/descriptive.ipynb")

    def test_search_token_uses_class_for_methods(self) -> None:
        """Method graduations search by class name; functions by function name."""
        assert (
            check_notebooks.search_token("src.models.linear_regression:LinearRegression.fit")
            == "LinearRegression"
        )
        assert (
            check_notebooks.search_token("src.statistics.descriptive:calculate_mean")
            == "calculate_mean"
        )

    def test_dedicated_test_matching(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """A reference outside the contract suites counts; inside them does not."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_stub_contracts.py").write_text(
            "calculate_mean\n", encoding="utf-8"
        )  # contract suite: must NOT count
        monkeypatch.setattr(check_notebooks, "TESTS_DIR", tests_dir)
        name = "src.statistics.descriptive:calculate_mean"
        assert not check_notebooks.has_dedicated_test(name)
        (tests_dir / "test_descriptive.py").write_text(
            "from src.statistics.descriptive import calculate_mean\n", encoding="utf-8"
        )
        assert check_notebooks.has_dedicated_test(name)
        # \b boundary: a superstring identifier must not satisfy the check
        (tests_dir / "test_descriptive.py").write_text(
            "import calculate_mean_manual\n", encoding="utf-8"
        )
        assert not check_notebooks.has_dedicated_test(name)
