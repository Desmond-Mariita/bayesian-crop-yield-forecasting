"""Unit tests for the graduated NASS acquisition function (src/data/acquisition.py).

Uses the bundled sample payload at ``data/samples/nass_quickstats_sample.json`` —
the same fixture the companion notebook demonstrates on. No network access.
"""

import json
import urllib.parse
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import pytest

from src.data.acquisition import (
    DATA_SOURCE_TAG,
    _build_query_url,
    _records_to_frame,
    download_nass_yields,
)

SAMPLE_PATH = Path("data/samples/nass_quickstats_sample.json")


@pytest.fixture()
def sample_payload() -> Dict[str, Any]:
    """Load the bundled Quick Stats sample payload.

    Returns:
        The decoded sample payload (5 county-year records, one suppressed).
    """
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


class TestBuildQueryUrl:
    """URL construction for the Quick Stats GET endpoint."""

    def test_url_carries_all_filters(self) -> None:
        """The URL pins commodity, start year, county-level survey yields, JSON."""
        url = _build_query_url(api_key="SECRET", crop="CORN", year_start=2000)
        query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        assert query == {
            "key": "SECRET",
            "commodity_desc": "CORN",
            "year__GE": "2000",
            "statisticcat_desc": "YIELD",
            "agg_level_desc": "COUNTY",
            "source_desc": "SURVEY",
            "format": "JSON",
        }


class TestRecordsToFrame:
    """Tidying the Quick Stats payload into the county-year yield table."""

    def test_tidies_columns_and_tags_source(self, sample_payload: Dict[str, Any]) -> None:
        """Every record keeps its keys, gains numeric yield and the data_source tag."""
        frame = _records_to_frame(sample_payload)
        assert list(frame.columns) == [
            "year",
            "state_alpha",
            "county_name",
            "county_ansi",
            "unit_desc",
            "yield_value",
            "data_source",
        ]
        assert len(frame) == 5
        assert (frame["data_source"] == DATA_SOURCE_TAG).all()

    def test_thousands_separator_is_stripped(self, sample_payload: Dict[str, Any]) -> None:
        """NASS values like "1,234" parse as numbers, not NaN."""
        frame = _records_to_frame(sample_payload)
        champaign = frame.loc[frame["county_name"] == "CHAMPAIGN", "yield_value"]
        assert champaign.item() == 1234.0

    def test_suppressed_values_become_nan(self, sample_payload: Dict[str, Any]) -> None:
        """Disclosure-suppressed "(D)" values coerce to NaN rather than erroring."""
        frame = _records_to_frame(sample_payload)
        suppressed = frame.loc[frame["county_ansi"] == "", "yield_value"]
        assert suppressed.isna().all()

    def test_error_payload_raises_connection_error(self) -> None:
        """The API signals errors as payloads without a data list."""
        with pytest.raises(ConnectionError, match="exceeds limit"):
            _records_to_frame({"error": ["exceeds limit of 50,000 records"]})


class TestDownloadNassYields:
    """The public entry point, with fetching stubbed out."""

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Without NASS_API_KEY (env or .env) the function refuses before any network use."""
        monkeypatch.delenv("NASS_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)  # guarantee no local .env can satisfy the lookup
        with pytest.raises(EnvironmentError, match="NASS_API_KEY"):
            download_nass_yields()

    def test_unknown_crop_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Only the supported commodities are accepted."""
        monkeypatch.setenv("NASS_API_KEY", "SECRET")
        with pytest.raises(ValueError, match="crop"):
            download_nass_yields(crop="BANANAS")

    def test_downloads_and_writes_tagged_csv(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Happy path: payload is tidied and saved; every row carries the tag."""
        monkeypatch.setenv("NASS_API_KEY", "SECRET")
        monkeypatch.setattr("src.data.acquisition._fetch_json", lambda url: sample_payload)
        output_path = download_nass_yields(crop="CORN", year_start=2021, output_dir=tmp_path)
        assert output_path == tmp_path / "nass_corn_yields.csv"
        saved = pd.read_csv(output_path)
        assert len(saved) == 5
        assert (saved["data_source"] == DATA_SOURCE_TAG).all()

    def test_fetch_failure_propagates(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """A failed request surfaces as ConnectionError, as documented."""
        monkeypatch.setenv("NASS_API_KEY", "SECRET")

        def boom(url: str) -> Dict[str, Any]:
            raise ConnectionError("NASS Quick Stats request failed: timeout")

        monkeypatch.setattr("src.data.acquisition._fetch_json", boom)
        with pytest.raises(ConnectionError, match="request failed"):
            download_nass_yields(output_dir=tmp_path)
