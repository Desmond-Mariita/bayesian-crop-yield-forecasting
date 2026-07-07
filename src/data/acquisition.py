"""
Data acquisition utilities for downloading and caching datasets.

This module handles downloading county-level crop yield data from the
USDA NASS Quick Stats API and daily weather data from the NASA POWER
agroclimatology API (curriculum decision: POWER is global, keyless, and
the same source the keragita-farm-intelligence platform consumes — the
acquisition code written here transfers directly to the Kilifi capstone).

Every record written by this module carries a ``data_source`` column —
``api_nass`` for Quick Stats rows, ``api_nasa_power`` for POWER rows —
mirroring the production platform's INV-006 "data source is always tagged"
rule (see ``docs/INVARIANTS.md`` LINV-005 companion practice and the cards
``docs/data_cards/DC-usda-nass-quickstats.md`` / ``DC-nasapower-weather.md``).
"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# =============================================================================
# CONSTANTS
# =============================================================================
NASS_API_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
CROPS = ("CORN", "SOYBEANS")
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"

API_KEY_ENV_VAR = "NASS_API_KEY"
DATA_SOURCE_TAG = "api_nass"
REQUEST_TIMEOUT_S = 60
# Quick Stats filters: county-level survey yields (not the 5-yearly census).
AGG_LEVEL = "COUNTY"
STATISTIC_CATEGORY = "YIELD"
SOURCE_DESC = "SURVEY"

# NASA POWER daily agroclimatology (AG community units: T2M degC, RH2M %,
# ALLSKY_SFC_SW_DWN MJ m^-2 day^-1, WS2M m s^-1).
POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
POWER_PARAMETERS = ("T2M", "T2M_MAX", "T2M_MIN", "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M")
POWER_COMMUNITY = "AG"
POWER_DATA_START_YEAR = 1981
POWER_FILL_VALUE = -999.0
POWER_DATA_SOURCE_TAG = "api_nasa_power"
LATITUDE_MIN, LATITUDE_MAX = -90.0, 90.0
LONGITUDE_MIN, LONGITUDE_MAX = -180.0, 180.0

logger = logging.getLogger(__name__)


def _build_query_url(api_key: str, crop: str, year_start: int) -> str:
    """Build the Quick Stats GET URL for county-level survey yields.

    Args:
        api_key: NASS API key (transmitted as the ``key`` query parameter).
        crop: Commodity name as used by NASS (e.g., "CORN").
        year_start: First harvest year to request (inclusive, ``year__GE``).

    Returns:
        The fully-encoded request URL.
    """
    params = {
        "key": api_key,
        "commodity_desc": crop,
        "year__GE": str(year_start),
        "statisticcat_desc": STATISTIC_CATEGORY,
        "agg_level_desc": AGG_LEVEL,
        "source_desc": SOURCE_DESC,
        "format": "JSON",
    }
    return f"{NASS_API_URL}?{urllib.parse.urlencode(params)}"


def _fetch_json(url: str) -> Dict[str, Any]:
    """Fetch a URL and decode its JSON body.

    Args:
        url: Request URL (may contain the API key — never log it).

    Returns:
        The decoded JSON payload.

    Raises:
        ConnectionError: If the request fails or the body is not valid JSON.
    """
    try:
        with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_S) as response:
            body = response.read()
    except urllib.error.URLError as exc:
        raise ConnectionError(f"API request failed: {exc}") from exc
    try:
        payload: Dict[str, Any] = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ConnectionError(f"API returned invalid JSON: {exc}") from exc
    return payload


def _records_to_frame(payload: Dict[str, Any]) -> pd.DataFrame:
    """Tidy a Quick Stats JSON payload into a county-year yield table.

    Args:
        payload: Decoded Quick Stats response; expected to hold a ``data`` list.

    Returns:
        DataFrame with columns ``year``, ``state_alpha``, ``county_name``,
        ``county_ansi``, ``unit_desc``, ``yield_value`` (numeric; NASS uses
        thousands separators, and suppressed values become NaN), and the
        mandatory ``data_source`` tag column.

    Raises:
        ConnectionError: If the payload has no ``data`` list (the API signals
            errors this way, e.g. bad key or unsupported query).
    """
    if "data" not in payload:
        raise ConnectionError(f"NASS Quick Stats error response: {payload}")
    frame = pd.DataFrame(payload["data"])
    columns = ["year", "state_alpha", "county_name", "county_ansi", "unit_desc", "Value"]
    absent = [c for c in columns if c not in frame.columns]
    if absent:
        logger.warning("NASS payload missing expected columns %s — check the API schema", absent)
    frame = frame.loc[:, [c for c in columns if c in frame.columns]].rename(
        columns={"Value": "yield_value"}
    )
    frame["yield_value"] = pd.to_numeric(
        frame["yield_value"].astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce",
    )
    frame["data_source"] = DATA_SOURCE_TAG
    return frame


def download_nass_yields(
    crop: str = "CORN",
    year_start: int = 1990,
    output_dir: Optional[Path] = None,
) -> Path:
    """Download county-level yield data from the USDA NASS Quick Stats API.

    Args:
        crop: Commodity name as used by NASS (e.g., "CORN", "SOYBEANS").
        year_start: First harvest year to request.
        output_dir: Directory to save the downloaded files (defaults to
            ``data/raw``; created if missing).

    Returns:
        Path to the downloaded file.

    Raises:
        EnvironmentError: If the NASS_API_KEY environment variable is not set.
        ValueError: If ``crop`` is not one of the supported ``CROPS``.
        ConnectionError: If download fails or the API returns an error payload.

    Note:
        Requires a free API key from https://quickstats.nass.usda.gov/api
        set as the NASS_API_KEY environment variable.
    """
    api_key = os.environ.get(API_KEY_ENV_VAR, "")
    if not api_key:
        raise EnvironmentError(f"{API_KEY_ENV_VAR} environment variable is not set")
    if crop not in CROPS:
        raise ValueError(f"crop must be one of {CROPS}, got {crop!r}")

    logger.info("requesting NASS %s county yields from %s onwards", crop, year_start)
    payload = _fetch_json(_build_query_url(api_key, crop, year_start))
    frame = _records_to_frame(payload)

    target_dir = output_dir if output_dir is not None else DATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"nass_{crop.lower()}_yields.csv"
    frame.to_csv(output_path, index=False)
    logger.info("saved %d NASS records to %s", len(frame), output_path)
    return output_path


def _build_power_url(latitude: float, longitude: float, year_start: int, year_end: int) -> str:
    """Build the NASA POWER daily-point GET URL for the agroclimatology parameters.

    Args:
        latitude: Point latitude in decimal degrees.
        longitude: Point longitude in decimal degrees.
        year_start: First calendar year (inclusive; request starts Jan 1).
        year_end: Last calendar year (inclusive; request ends Dec 31).

    Returns:
        The fully-encoded request URL.
    """
    params = {
        "parameters": ",".join(POWER_PARAMETERS),
        "community": POWER_COMMUNITY,
        "latitude": str(latitude),
        "longitude": str(longitude),
        "start": f"{year_start}0101",
        "end": f"{year_end}1231",
        "format": "JSON",
    }
    return f"{POWER_API_URL}?{urllib.parse.urlencode(params)}"


def _power_to_frame(payload: Dict[str, Any], latitude: float, longitude: float) -> pd.DataFrame:
    """Tidy a NASA POWER daily-point payload into a date-indexed weather table.

    Args:
        payload: Decoded POWER response; expected to hold
            ``properties.parameter.<PARAM>`` date→value mappings.
        latitude: Point latitude, recorded on every row for later joins.
        longitude: Point longitude, recorded on every row.

    Returns:
        DataFrame with a ``date`` column, one numeric column per parameter in
        ``POWER_PARAMETERS`` (the API's -999 fill value becomes NaN — a missing-data
        indicator, never a dropped row), ``latitude``, ``longitude``, and the
        mandatory ``data_source`` tag column.

    Raises:
        ConnectionError: If the payload lacks the ``properties.parameter`` block
            (POWER signals errors this way).
    """
    parameter_block = payload.get("properties", {}).get("parameter")
    if not parameter_block:
        raise ConnectionError(f"NASA POWER error response: {payload}")
    frame = pd.DataFrame(parameter_block)
    frame = frame.replace(POWER_FILL_VALUE, float("nan"))
    frame.insert(0, "date", pd.to_datetime(frame.index, format="%Y%m%d"))
    frame = frame.reset_index(drop=True)
    frame["latitude"] = latitude
    frame["longitude"] = longitude
    frame["data_source"] = POWER_DATA_SOURCE_TAG
    return frame


def download_weather_data(
    latitude: float,
    longitude: float,
    year_start: int,
    year_end: int,
    output_dir: Optional[Path] = None,
) -> Path:
    """Download daily weather data for a point from the NASA POWER API.

    Curriculum decision: NASA POWER (agroclimatology community) rather than
    NOAA/PRISM — it is global and keyless, provides the temperature/humidity/
    solar/wind set the yield models need, and is the same source the production
    platform consumes, so this function is reused verbatim for the Kilifi
    capstone (Gongoni cell) in Phase 4. Note POWER carries no precipitation-
    gauge product here; rainfall joins later from CHIRPS.

    Args:
        latitude: Point latitude in decimal degrees (e.g. a county centroid).
        longitude: Point longitude in decimal degrees.
        year_start: First calendar year to request (POWER data starts 1981).
        year_end: Last calendar year to request (inclusive).
        output_dir: Directory to save the downloaded files (defaults to
            ``data/raw``; created if missing).

    Returns:
        Path to the downloaded file.

    Raises:
        ValueError: If coordinates are out of range or the year window is
            invalid (validated before any network use).
        ConnectionError: If download fails or the API returns an error payload.
    """
    if year_start < POWER_DATA_START_YEAR:
        raise ValueError(f"year_start must be >= {POWER_DATA_START_YEAR}, got {year_start}")
    if year_end < year_start:
        raise ValueError(f"year_end ({year_end}) must be >= year_start ({year_start})")
    if not LATITUDE_MIN <= latitude <= LATITUDE_MAX:
        raise ValueError(f"latitude must be in [{LATITUDE_MIN}, {LATITUDE_MAX}], got {latitude}")
    if not LONGITUDE_MIN <= longitude <= LONGITUDE_MAX:
        raise ValueError(
            f"longitude must be in [{LONGITUDE_MIN}, {LONGITUDE_MAX}], got {longitude}"
        )

    logger.info(
        "requesting NASA POWER daily weather for (%s, %s), %s-%s",
        latitude,
        longitude,
        year_start,
        year_end,
    )
    payload = _fetch_json(_build_power_url(latitude, longitude, year_start, year_end))
    frame = _power_to_frame(payload, latitude=latitude, longitude=longitude)

    target_dir = output_dir if output_dir is not None else DATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"nasa_power_daily_{year_start}_{year_end}.csv"
    frame.to_csv(output_path, index=False)
    logger.info("saved %d NASA POWER records to %s", len(frame), output_path)
    return output_path
