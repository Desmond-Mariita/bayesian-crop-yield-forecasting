"""Unit tests for the graduated NASA POWER weather function (src/data/acquisition.py).

Uses the bundled sample payload at ``data/samples/nasa_power_sample.json`` — the same
fixture the companion notebook demonstrates on. No network access.
"""

import json
import urllib.parse
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import pytest

from src.data.acquisition import (
    POWER_DATA_SOURCE_TAG,
    POWER_PARAMETERS,
    _build_power_url,
    _power_to_frame,
    download_weather_data,
)

SAMPLE_PATH = Path("data/samples/nasa_power_sample.json")
AMES_LAT, AMES_LON = 42.03, -93.62


@pytest.fixture()
def sample_payload() -> Dict[str, Any]:
    """Load the bundled POWER sample payload.

    Returns:
        The decoded sample payload (3 days, 6 parameters, one -999 fill value).
    """
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


class TestBuildPowerUrl:
    """URL construction for the POWER daily-point endpoint."""

    def test_url_carries_all_parameters_and_window(self) -> None:
        """The URL pins the parameter set, AG community, point, and date window."""
        url = _build_power_url(
            latitude=AMES_LAT, longitude=AMES_LON, year_start=2020, year_end=2021
        )
        query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        assert query["parameters"] == ",".join(POWER_PARAMETERS)
        assert query["community"] == "AG"
        assert query["latitude"] == str(AMES_LAT)
        assert query["longitude"] == str(AMES_LON)
        assert query["start"] == "20200101"
        assert query["end"] == "20211231"
        assert query["format"] == "JSON"


class TestPowerToFrame:
    """Tidying the POWER payload into the daily weather table."""

    def test_tidies_columns_and_tags_source(self, sample_payload: Dict[str, Any]) -> None:
        """One row per day, one column per parameter, coordinates and tag on every row."""
        frame = _power_to_frame(sample_payload, latitude=AMES_LAT, longitude=AMES_LON)
        assert list(frame.columns) == [
            "date",
            *POWER_PARAMETERS,
            "latitude",
            "longitude",
            "data_source",
        ]
        assert len(frame) == 3
        assert (frame["data_source"] == POWER_DATA_SOURCE_TAG).all()
        assert (frame["latitude"] == AMES_LAT).all()

    def test_dates_parse_from_compact_format(self, sample_payload: Dict[str, Any]) -> None:
        """POWER's YYYYMMDD keys become real timestamps."""
        frame = _power_to_frame(sample_payload, latitude=AMES_LAT, longitude=AMES_LON)
        assert frame["date"].iloc[0] == pd.Timestamp("2021-06-01")

    def test_fill_values_become_nan(self, sample_payload: Dict[str, Any]) -> None:
        """The -999 fill value is a missing-data indicator, not a real humidity."""
        frame = _power_to_frame(sample_payload, latitude=AMES_LAT, longitude=AMES_LON)
        assert frame["RH2M"].isna().sum() == 1
        assert frame["RH2M"].min() > 0  # no -999 leaked through as data

    def test_error_payload_raises_connection_error(self) -> None:
        """POWER signals errors as payloads without properties.parameter."""
        with pytest.raises(ConnectionError, match="POWER error"):
            _power_to_frame({"messages": ["invalid parameters"]}, latitude=0.0, longitude=0.0)


class TestDownloadWeatherData:
    """The public entry point: validation happens before any network use."""

    @pytest.mark.parametrize(
        ("kwargs", "match"),
        [
            (
                {"latitude": 91.0, "longitude": 0.0, "year_start": 2000, "year_end": 2001},
                "latitude",
            ),
            (
                {"latitude": 0.0, "longitude": 181.0, "year_start": 2000, "year_end": 2001},
                "longitude",
            ),
            (
                {"latitude": 0.0, "longitude": 0.0, "year_start": 1979, "year_end": 2001},
                "year_start",
            ),
            ({"latitude": 0.0, "longitude": 0.0, "year_start": 2005, "year_end": 2001}, "year_end"),
        ],
    )
    def test_invalid_inputs_rejected_before_network(self, kwargs: dict, match: str) -> None:
        """Bad coordinates or year windows raise ValueError with no request made."""
        with pytest.raises(ValueError, match=match):
            download_weather_data(**kwargs)

    def test_downloads_and_writes_tagged_csv(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        sample_payload: Dict[str, Any],
    ) -> None:
        """Happy path: payload is tidied and saved; every row carries the tag."""
        monkeypatch.setattr("src.data.acquisition._fetch_json", lambda url: sample_payload)
        output_path = download_weather_data(
            latitude=AMES_LAT,
            longitude=AMES_LON,
            year_start=2021,
            year_end=2021,
            output_dir=tmp_path,
        )
        assert output_path == tmp_path / "nasa_power_daily_2021_2021.csv"
        saved = pd.read_csv(output_path)
        assert len(saved) == 3
        assert (saved["data_source"] == POWER_DATA_SOURCE_TAG).all()

    def test_fetch_failure_propagates(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """A failed request surfaces as ConnectionError, as documented."""

        def boom(url: str) -> Dict[str, Any]:
            raise ConnectionError("NASS Quick Stats request failed: timeout")

        monkeypatch.setattr("src.data.acquisition._fetch_json", boom)
        with pytest.raises(ConnectionError, match="request failed"):
            download_weather_data(
                latitude=AMES_LAT,
                longitude=AMES_LON,
                year_start=2021,
                year_end=2021,
                output_dir=tmp_path,
            )
