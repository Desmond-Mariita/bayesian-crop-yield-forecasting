#!/usr/bin/env python3
"""Companion-notebook enforcement gate (LINV-010).

Every *graduated* curriculum module — one with at least one implemented callable — must
ship a companion notebook at the mirrored path under ``notebooks/`` (e.g.
``src/statistics/descriptive.py`` → ``notebooks/statistics/descriptive.ipynb``). The
notebook explains motivation and mathematics and displays the shipped source via
``inspect.getsource`` — it never carries a hand-maintained copy of the code.

The single source of truth for graduation is the ``IMPLEMENTED`` ledger in
``tests/unit/test_stub_contracts.py`` (qualified names like
``src.statistics.descriptive:calculate_mean``). This tool reads that ledger via AST, so
graduating a stub automatically demands its module's notebook. Infrastructure modules
(e.g. ``src/xai``) are outside the curriculum ledger and therefore exempt unless listed
in ``EXTRA_MODULES``.

Pure standard library; exits non-zero on any violation.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import FrozenSet, List

LEDGER_PATH: Path = Path("tests/unit/test_stub_contracts.py")
LEDGER_NAME: str = "IMPLEMENTED"
NOTEBOOKS_DIR: Path = Path("notebooks")
SRC_PREFIX: str = "src."

# Non-curriculum modules that must ALSO ship a companion notebook (explicit opt-in).
EXTRA_MODULES: FrozenSet[str] = frozenset()


def read_graduation_ledger(ledger_path: Path) -> FrozenSet[str]:
    """Read the ``IMPLEMENTED`` frozenset from the stub-contract test module.

    Args:
        ledger_path: Path to the test module holding the ledger.

    Returns:
        The qualified callable names recorded as implemented.

    Raises:
        ValueError: If the ledger file or the ``IMPLEMENTED`` assignment is missing or
            not a literal ``frozenset(...)`` call.
    """
    if not ledger_path.is_file():
        raise ValueError(f"graduation ledger not found: {ledger_path}")
    tree = ast.parse(ledger_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            first = node.targets[0]
            target = first.id if isinstance(first, ast.Name) else None
        if target != LEDGER_NAME or node.value is None:
            continue
        value = node.value
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
        ):
            if not value.args:
                return frozenset()
            return frozenset(ast.literal_eval(value.args[0]))
        raise ValueError(f"{LEDGER_NAME} must be assigned a literal frozenset(...) call")
    raise ValueError(f"no {LEDGER_NAME} assignment found in {ledger_path}")


def graduated_modules(ledger: FrozenSet[str]) -> FrozenSet[str]:
    """Extract the module part of every graduated qualified name.

    Args:
        ledger: Qualified names like ``src.statistics.descriptive:calculate_mean``.

    Returns:
        The dotted module paths containing at least one implemented callable.
    """
    return frozenset(name.partition(":")[0] for name in ledger)


def expected_notebook(module: str) -> Path:
    """Return the mirrored companion-notebook path for a module.

    Args:
        module: Dotted module path (e.g. ``src.statistics.descriptive``).

    Returns:
        The required notebook path (e.g. ``notebooks/statistics/descriptive.ipynb``).
    """
    relative = module.removeprefix(SRC_PREFIX).replace(".", "/")
    return NOTEBOOKS_DIR / f"{relative}.ipynb"


def main() -> int:
    """Check every graduated module for its companion notebook and report the verdict.

    Returns:
        0 when every required notebook exists (or nothing has graduated yet), 1 on any
        missing notebook or an unreadable ledger.
    """
    parser = argparse.ArgumentParser(description="companion-notebook gate (LINV-010)")
    parser.add_argument(
        "--ledger", default=str(LEDGER_PATH), help="Path to the stub-contract test module"
    )
    args = parser.parse_args()

    write = sys.stdout.write
    try:
        ledger = read_graduation_ledger(Path(args.ledger))
    except ValueError as exc:
        write(f"VIOLATION: {exc}\n")
        write("notebooks gate: FAIL (unreadable graduation ledger)\n")
        return 1

    required = sorted(graduated_modules(ledger) | EXTRA_MODULES)
    if not required:
        write("no curriculum modules graduated yet — notebooks gate trivially green\n")
        return 0

    missing: List[str] = []
    for module in required:
        notebook = expected_notebook(module)
        if not notebook.is_file():
            missing.append(f"{module} → expected companion notebook {notebook}")
    if missing:
        for entry in missing:
            write(f"VIOLATION: missing notebook: {entry}\n")
        write(f"notebooks gate: FAIL ({len(missing)} missing)\n")
        return 1
    write(f"notebooks gate: PASS ({len(required)} module(s) with companion notebooks)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
