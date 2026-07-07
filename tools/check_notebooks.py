#!/usr/bin/env python3
"""Graduation gate: companion notebooks (LINV-010) + dedicated tests per graduation.

For every *graduated* curriculum callable — a qualified name in ``IMPLEMENTED`` in
``src/curriculum_ledger.py`` (the single-source-of-truth ledger, imported directly) —
this gate enforces two things:

1. **Companion notebook** (LINV-010): the module ships a notebook at the mirrored path
   under ``notebooks/`` (e.g. ``src/statistics/descriptive.py`` →
   ``notebooks/statistics/descriptive.ipynb``).
2. **Dedicated tests**: the graduated callable is referenced in at least one test file
   OUTSIDE the stub-contract suites. The global coverage gate is only a backstop — this
   check mechanically requires per-graduation tests (the panel's convergent Major).

Infrastructure modules (outside the curriculum stub ledger, e.g. ``src/xai``) are exempt
unless opted into ``EXTRA_MODULES``. Pure standard library; exits non-zero on violation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import FrozenSet, List

REPO_ROOT: Path = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR: Path = Path("notebooks")
TESTS_DIR: Path = Path("tests")
SRC_PREFIX: str = "src."

# Contract suites do not count as dedicated tests for a graduated callable.
CONTRACT_SUITES: FrozenSet[str] = frozenset(
    {"test_stub_contracts.py", "test_stub_private_branches.py"}
)

# Non-curriculum modules that must ALSO ship a companion notebook (explicit opt-in).
EXTRA_MODULES: FrozenSet[str] = frozenset()


def load_ledger() -> FrozenSet[str]:
    """Import the graduation ledger from ``src/curriculum_ledger.py``.

    Returns:
        The qualified callable names recorded as implemented.

    Raises:
        ValueError: If the ledger module cannot be imported.
    """
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from src.curriculum_ledger import IMPLEMENTED
    except Exception as exc:  # pragma: no cover - defensive: broken ledger must FAIL CI
        raise ValueError(f"cannot import graduation ledger (src/curriculum_ledger.py): {exc}")
    return frozenset(IMPLEMENTED)


def expected_notebook(module: str) -> Path:
    """Return the mirrored companion-notebook path for a module.

    Args:
        module: Dotted module path (e.g. ``src.statistics.descriptive``).

    Returns:
        The required notebook path (e.g. ``notebooks/statistics/descriptive.ipynb``).
    """
    relative = module.removeprefix(SRC_PREFIX).replace(".", "/")
    return NOTEBOOKS_DIR / f"{relative}.ipynb"


def search_token(qualified_name: str) -> str:
    """Return the identifier a dedicated test must reference for a graduated name.

    Functions use the function name; methods use the class name (method tokens like
    ``fit`` are too generic to search for reliably).

    Args:
        qualified_name: Ledger entry such as ``src.models.linear_regression:LinearRegression.fit``.

    Returns:
        The identifier to search for in test files.
    """
    callable_part = qualified_name.partition(":")[2]
    return callable_part.split(".")[0]


def has_dedicated_test(qualified_name: str) -> bool:
    """Return whether a graduated callable is referenced outside the contract suites.

    Args:
        qualified_name: Ledger entry to check.

    Returns:
        True if some non-contract test file mentions the callable's search token.
    """
    pattern = re.compile(rf"\b{re.escape(search_token(qualified_name))}\b")
    for test_file in sorted(TESTS_DIR.rglob("test_*.py")):
        if test_file.name in CONTRACT_SUITES:
            continue
        if pattern.search(test_file.read_text(encoding="utf-8")):
            return True
    return False


def main() -> int:
    """Run the graduation gate and report the verdict.

    Returns:
        0 when every graduated name has its notebook and a dedicated test (or nothing
        has graduated yet), 1 on any violation.
    """
    write = sys.stdout.write
    try:
        ledger = load_ledger()
    except ValueError as exc:
        write(f"VIOLATION: {exc}\n")
        write("graduation gate: FAIL (unreadable ledger)\n")
        return 1

    modules = sorted(frozenset(name.partition(":")[0] for name in ledger) | EXTRA_MODULES)
    if not modules:
        write("no curriculum modules graduated yet — graduation gate trivially green\n")
        return 0

    violations: List[str] = []
    for module in modules:
        notebook = expected_notebook(module)
        if not notebook.is_file():
            violations.append(f"missing notebook: {module} → expected {notebook}")
    for name in sorted(ledger):
        if not has_dedicated_test(name):
            violations.append(
                f"missing dedicated test: {name} is graduated but no test file outside "
                f"the contract suites references '{search_token(name)}'"
            )
    if violations:
        for violation in violations:
            write(f"VIOLATION: {violation}\n")
        write(f"graduation gate: FAIL ({len(violations)} violation(s))\n")
        return 1
    write(
        f"graduation gate: PASS ({len(modules)} module(s), {len(ledger)} graduated "
        "name(s) with notebooks and dedicated tests)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
