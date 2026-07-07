"""Integration smoke test: the full acquisition path through a fake HTTP layer.

Exercises ``_fetch_json``'s real wiring (urlopen call, JSON decode, error mapping)
without network access, then the end-to-end download flow on top of it.
"""

import io
import json
import urllib.error
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from src.data.acquisition import DATA_SOURCE_TAG, download_nass_yields

SAMPLE_PATH = Path("data/samples/nass_quickstats_sample.json")


class FakeResponse(io.BytesIO):
    """Minimal context-manager stand-in for urlopen's response object."""

    def __enter__(self) -> "FakeResponse":
        """Enter the context.

        Returns:
            This response object.
        """
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Exit the context, closing the buffer."""
        self.close()


def test_end_to_end_download_via_fake_http(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The whole path — urlopen, JSON decode, tidy, tag, save — works together."""
    body = SAMPLE_PATH.read_bytes()
    seen_urls = []

    def fake_urlopen(url: str, timeout: float) -> FakeResponse:
        seen_urls.append(url)
        return FakeResponse(body)

    monkeypatch.setenv("NASS_API_KEY", "SECRET")
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    output_path = download_nass_yields(crop="SOYBEANS", year_start=2021, output_dir=tmp_path)

    assert "commodity_desc=SOYBEANS" in seen_urls[0]
    saved = pd.read_csv(output_path)
    assert len(saved) == len(json.loads(body)["data"])
    assert (saved["data_source"] == DATA_SOURCE_TAG).all()


def test_http_failure_maps_to_connection_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """URLError from the HTTP layer surfaces as the documented ConnectionError."""

    def fake_urlopen(url: str, timeout: float) -> FakeResponse:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setenv("NASS_API_KEY", "SECRET")
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(ConnectionError, match="request failed"):
        download_nass_yields(output_dir=tmp_path)


def test_invalid_json_maps_to_connection_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A non-JSON body surfaces as the documented ConnectionError."""

    def fake_urlopen(url: str, timeout: float) -> FakeResponse:
        return FakeResponse(b"<html>gateway timeout</html>")

    monkeypatch.setenv("NASS_API_KEY", "SECRET")
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(ConnectionError, match="invalid JSON"):
        download_nass_yields(output_dir=tmp_path)
