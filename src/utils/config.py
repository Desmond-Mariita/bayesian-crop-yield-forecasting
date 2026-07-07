"""Centralised configuration access with ``.env`` support (DEVELOPER_GUIDELINES §4).

Single lookup path for secrets and settings: the process environment wins, a local
``.env`` file (gitignored, ``KEY=VALUE`` lines) is the fallback. Nothing here ever
logs a value — configuration values are assumed secret unless proven otherwise.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional

ENV_FILE = Path(".env")
COMMENT_PREFIX = "#"

logger = logging.getLogger(__name__)


def _parse_env_file(env_file: Path) -> Dict[str, str]:
    """Parse a ``.env`` file into a mapping.

    Supported syntax: ``KEY=VALUE`` lines, blank lines, and ``#`` comment lines.
    Values may be single- or double-quoted; quotes are stripped.

    Args:
        env_file: Path to the ``.env`` file; a missing file yields an empty mapping.

    Returns:
        Mapping of variable name to value.
    """
    if not env_file.is_file():
        return {}
    values: Dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(COMMENT_PREFIX) or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip().strip("\"'")
    return values


def get_env(
    name: str,
    default: Optional[str] = None,
    required: bool = False,
    env_file: Path = ENV_FILE,
) -> Optional[str]:
    """Look up a configuration value: process environment first, ``.env`` fallback.

    Args:
        name: Variable name (e.g. ``NASS_API_KEY``).
        default: Value returned when the variable is set nowhere.
        required: When True, an unset variable raises instead of returning ``default``.
        env_file: ``.env`` file to fall back to (injectable for tests).

    Returns:
        The value, or ``default`` when unset and not required.

    Raises:
        EnvironmentError: If ``required`` is True and the variable is set neither in
            the environment nor in the ``.env`` file.

    Note:
        An EMPTY value (``KEY=`` in the environment or ``.env``) is deliberately
        treated as unset: an empty API key is never useful, and failing loudly beats
        sending blank credentials.
    """
    value = os.environ.get(name)
    source = "environment"
    if value is None:
        value = _parse_env_file(env_file).get(name)
        source = str(env_file)
    if value:
        logger.debug("config: %s loaded from %s", name, source)
        return value
    if required:
        raise EnvironmentError(f"{name} environment variable is not set (checked env and .env)")
    return default
