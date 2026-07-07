"""Unit tests for the centralised configuration lookup (src/utils/config.py)."""

from pathlib import Path

import pytest

from src.utils.config import _parse_env_file, get_env


class TestParseEnvFile:
    """The minimal .env parser."""

    def test_missing_file_yields_empty_mapping(self, tmp_path: Path) -> None:
        """A missing .env is not an error — just no fallback values."""
        assert _parse_env_file(tmp_path / ".env") == {}

    def test_parses_pairs_comments_and_quotes(self, tmp_path: Path) -> None:
        """KEY=VALUE lines parse; comments/blanks skip; quotes strip."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# secrets\n\nNASS_API_KEY=abc123\nQUOTED='hello world'\nDOUBLE=\"x=y\"\n",
            encoding="utf-8",
        )
        parsed = _parse_env_file(env_file)
        assert parsed["NASS_API_KEY"] == "abc123"
        assert parsed["QUOTED"] == "hello world"
        assert parsed["DOUBLE"] == "x=y"


class TestGetEnv:
    """Lookup precedence and the required contract."""

    def test_environment_wins_over_env_file(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """A real environment variable beats the .env fallback."""
        env_file = tmp_path / ".env"
        env_file.write_text("MY_KEY=from_file\n", encoding="utf-8")
        monkeypatch.setenv("MY_KEY", "from_env")
        assert get_env("MY_KEY", env_file=env_file) == "from_env"

    def test_env_file_fallback(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """When the environment is unset, the .env file supplies the value."""
        env_file = tmp_path / ".env"
        env_file.write_text("MY_KEY=from_file\n", encoding="utf-8")
        monkeypatch.delenv("MY_KEY", raising=False)
        assert get_env("MY_KEY", env_file=env_file) == "from_file"

    def test_default_when_unset(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Unset and not required returns the default."""
        monkeypatch.delenv("MY_KEY", raising=False)
        assert get_env("MY_KEY", default="fallback", env_file=tmp_path / ".env") == "fallback"

    def test_required_and_unset_raises(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """required=True turns absence into the documented EnvironmentError."""
        monkeypatch.delenv("MY_KEY", raising=False)
        with pytest.raises(EnvironmentError, match="MY_KEY"):
            get_env("MY_KEY", required=True, env_file=tmp_path / ".env")


def test_acquisition_accepts_env_file_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Integration: a .env-supplied key satisfies download_nass_yields' key check.

    The fetch is stubbed; this pins the config wiring, not the network.
    """
    import json

    from src.data import acquisition

    sample = json.loads(Path("data/samples/nass_quickstats_sample.json").read_text())
    monkeypatch.delenv("NASS_API_KEY", raising=False)
    (tmp_path / ".env").write_text("NASS_API_KEY=from_dotenv\n", encoding="utf-8")
    monkeypatch.setattr(acquisition, "_fetch_json", lambda url: sample)
    monkeypatch.chdir(tmp_path)
    output_path = acquisition.download_nass_yields(output_dir=tmp_path)
    assert output_path.is_file()
