"""
Data loading utilities for the bayesian-crop-yield-forecasting project.

This module provides functions to load and validate the assembled
county x year crop yield dataset (USDA NASS yields joined with weather).
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import pandas as pd

# =============================================================================
# CONSTANTS
# =============================================================================
DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "raw"
TARGET_COLUMN = "yield_bu_per_acre"
DEFAULT_DTYPES = {
    "state_fips": str,
    "county_fips": str,
    "county_name": str,
    "crop": str,
    "year": int,
    "yield_bu_per_acre": float,
    "harvested_acres": float,
    "irrigated": str,
}


def load_yield_data(
    filepath: Optional[Union[str, Path]] = None,
    nrows: Optional[int] = None,
    usecols: Optional[list] = None,
) -> pd.DataFrame:
    """
    Load the county-level crop yield dataset.

    Args:
        filepath: Path to the CSV file. If None, looks in default data directory.
        nrows: Number of rows to load. If None, loads all rows.
        usecols: List of columns to load. If None, loads all columns.

    Returns:
        DataFrame containing county x year yield and weather observations.

    Raises:
        FileNotFoundError: If the data file is not found.
        ValueError: If the file is empty or corrupted.

    Example:
        >>> df = load_yield_data(nrows=1000)
        >>> print(df.shape)
        (1000, 25)
    """
    # TODO: Implement in Week 1
    raise NotImplementedError("Implement this function in Week 1")


def validate_data(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Validate the loaded dataset for expected structure and content.

    Args:
        df: DataFrame to validate.

    Returns:
        Tuple of (is_valid, list_of_issues).

    Raises:
        TypeError: If input is not a DataFrame.
    """
    # TODO: Implement in Week 1
    raise NotImplementedError("Implement this function in Week 1")


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate a summary of the dataset.

    Args:
        df: DataFrame to summarize.

    Returns:
        Dictionary containing shape, dtypes, memory usage, etc.
    """
    # TODO: Implement in Week 1
    raise NotImplementedError("Implement this function in Week 1")
