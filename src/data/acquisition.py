"""
Data acquisition utilities for downloading and caching datasets.

This module handles downloading county-level crop yield data from the
USDA NASS Quick Stats API and growing-season weather data from public
sources (NOAA / PRISM).

Every record written by this module carries a ``data_source`` column
(``api_nass``) — mirroring the production platform's INV-006 "data source
is always tagged" rule (see ``docs/INVARIANTS.md`` LINV-005 companion
practice and ``docs/data_cards/DC-usda-nass-quickstats.md``).
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
        raise ConnectionError(f"NASS Quick Stats request failed: {exc}") from exc
    try:
        payload: Dict[str, Any] = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ConnectionError(f"NASS Quick Stats returned invalid JSON: {exc}") from exc
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


def download_weather_data(
    year_start: int = 1990,
    output_dir: Optional[Path] = None,
) -> Path:
    """
    Download county-aggregated growing-season weather data (NOAA/PRISM).

    Args:
        year_start: First year to request.
        output_dir: Directory to save the downloaded files.

    Returns:
        Path to the downloaded file.

    Raises:
        ConnectionError: If download fails.
    """
    # TODO: Implement in Week 1
    raise NotImplementedError("Implement this function in Week 1")
