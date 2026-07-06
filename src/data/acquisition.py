"""
Data acquisition utilities for downloading and caching datasets.

This module handles downloading county-level crop yield data from the
USDA NASS Quick Stats API and growing-season weather data from public
sources (NOAA / PRISM).
"""

from pathlib import Path
from typing import Optional

# =============================================================================
# CONSTANTS
# =============================================================================
NASS_API_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
CROPS = ("CORN", "SOYBEANS")
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"


def download_nass_yields(
    crop: str = "CORN",
    year_start: int = 1990,
    output_dir: Optional[Path] = None,
) -> Path:
    """
    Download county-level yield data from the USDA NASS Quick Stats API.

    Args:
        crop: Commodity name as used by NASS (e.g., "CORN", "SOYBEANS").
        year_start: First harvest year to request.
        output_dir: Directory to save the downloaded files.

    Returns:
        Path to the downloaded file.

    Raises:
        EnvironmentError: If the NASS_API_KEY environment variable is not set.
        ConnectionError: If download fails.

    Note:
        Requires a free API key from https://quickstats.nass.usda.gov/api
        set as the NASS_API_KEY environment variable.
    """
    # TODO: Implement in Week 1
    raise NotImplementedError("Implement this function in Week 1")


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
