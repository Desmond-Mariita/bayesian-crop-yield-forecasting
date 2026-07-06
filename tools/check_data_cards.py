#!/usr/bin/env python3
"""Data-card enforcement gate (LINV-005) — governance by CI, not aspiration.

Validates every ``docs/data_cards/DC-*.md`` against the required schema, adapted from
keragita-farm-intelligence's data cards. A card is YAML frontmatter (between ``---``
fences) followed by a Markdown body. Pure standard library — no third-party dependencies
— so it runs identically in CI, in hooks, and locally. Exits non-zero on any violation.

The frontmatter parser is deliberately minimal: ``key: value`` scalars and block lists
(``key:`` followed by ``  - item`` lines). Anything fancier should be simplified in the
card, not supported here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

FieldValue = Union[str, List[str]]

REQUIRED_SCALAR_FIELDS: Tuple[str, ...] = (
    "dataset_id",
    "dataset_name",
    "version",
    "status",
    "data_source_tag",
    "source_url",
    "collection_method",
    "date_range",
    "geographic_scope",
    "temporal_resolution",
    "phase",
)
REQUIRED_LIST_FIELDS: Tuple[str, ...] = ("known_limitations", "intended_use")
ALLOWED_STATUS: Tuple[str, ...] = ("draft", "approved")
FRONTMATTER_FENCE: str = "---"


def parse_frontmatter(text: str) -> Dict[str, FieldValue]:
    """Parse the YAML frontmatter block of a data card.

    Args:
        text: Full text of the card file.

    Returns:
        Mapping of frontmatter key to scalar string or list of strings.

    Raises:
        ValueError: If the frontmatter fences are missing or a line is unparseable.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_FENCE:
        raise ValueError("card must start with a '---' frontmatter fence")
    fields: Dict[str, FieldValue] = {}
    current_list_key = None
    for index, line in enumerate(lines[1:], start=2):
        stripped = line.strip()
        if stripped == FRONTMATTER_FENCE:
            return fields
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current_list_key is None:
                raise ValueError(f"line {index}: list item outside a list field")
            existing = fields[current_list_key]
            assert isinstance(existing, list)
            existing.append(stripped[2:].strip())
            continue
        if ":" not in stripped:
            raise ValueError(f"line {index}: expected 'key: value', got {stripped!r}")
        key, _, value = stripped.partition(":")
        key, value = key.strip(), value.strip().strip("\"'")
        if value:
            fields[key] = value
            current_list_key = None
        else:
            fields[key] = []
            current_list_key = key
    raise ValueError("frontmatter never closed with a '---' fence")


def validate_card(path: Path) -> List[str]:
    """Validate one data card against the required schema.

    Args:
        path: Path to the card file.

    Returns:
        Human-readable violation messages; empty when the card is valid.
    """
    try:
        fields = parse_frontmatter(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{path}: {exc}"]
    violations = []
    for field_name in REQUIRED_SCALAR_FIELDS:
        value = fields.get(field_name)
        if not isinstance(value, str) or not value:
            violations.append(f"{path}: missing or empty required field '{field_name}'")
    for field_name in REQUIRED_LIST_FIELDS:
        value = fields.get(field_name)
        if not isinstance(value, list) or not value:
            violations.append(f"{path}: '{field_name}' must be a non-empty list")
    status = fields.get("status")
    if isinstance(status, str) and status and status not in ALLOWED_STATUS:
        violations.append(f"{path}: status must be one of {ALLOWED_STATUS}, got '{status}'")
    return violations


def main() -> int:
    """Validate every data card and report the verdict.

    Returns:
        0 when every card is valid (or none exist yet), 1 on any violation.
    """
    parser = argparse.ArgumentParser(description="data-card enforcement gate (LINV-005)")
    parser.add_argument("--cards-dir", default="docs/data_cards", help="Data cards directory")
    args = parser.parse_args()

    cards_dir = Path(args.cards_dir)
    cards = sorted(cards_dir.glob("DC-*.md")) if cards_dir.is_dir() else []
    write = sys.stdout.write
    if not cards:
        write(f"no data cards found under {cards_dir} — nothing to validate yet\n")
        return 0

    all_violations: List[str] = []
    for card in cards:
        all_violations.extend(validate_card(card))
    if all_violations:
        for violation in all_violations:
            write(f"VIOLATION: {violation}\n")
        write(f"data-cards gate: FAIL ({len(all_violations)} violation(s))\n")
        return 1
    write(f"data-cards gate: PASS ({len(cards)} card(s) valid)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
