#!/usr/bin/env python3
"""Developer-guidelines enforcement gate (CI + pre-commit).

Enforces the mechanically-checkable subset of ``docs/DEVELOPER_GUIDELINES.txt`` over the
given paths (default: ``src``). Pure standard library — no third-party dependencies — so it
runs identically in CI, in a git pre-commit hook, and locally. Exits non-zero on any
violation so it fails the build / blocks the commit.

Enforced rules (from DEVELOPER_GUIDELINES.txt §3 Code Quality and §4 Architecture):
  * Google-style docstrings on every public function/class/method — ``Args:`` required when
    the function has non-self/cls parameters; ``Returns:`` required when it has a non-None
    return annotation.
  * PEP 484 type hints on every public function's parameters and its return.
  * No ``print(...)`` calls (use the ``logging`` module).
  * No wildcard ``from x import *``; module-level imports must sit at the top of the file.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Tuple, Union

Violation = Tuple[str, int, str]
FuncNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


def _non_self_args(node: FuncNode) -> List[ast.arg]:
    """Return a function's arguments excluding ``self``/``cls``.

    Args:
        node: Function definition node.

    Returns:
        The parameter nodes that are not ``self`` or ``cls``.
    """
    a = node.args
    return [
        arg for arg in (a.posonlyargs + a.args + a.kwonlyargs) if arg.arg not in {"self", "cls"}
    ]


def _has_non_none_return(node: FuncNode) -> bool:
    """Return whether a function declares a non-None return annotation.

    Args:
        node: Function definition node.

    Returns:
        True if the return annotation exists and is not ``None``.
    """
    r = node.returns
    if r is None:
        return False
    if isinstance(r, ast.Constant) and r.value is None:
        return False
    if isinstance(r, ast.Name) and r.id == "None":
        return False
    return True


def _public(name: str) -> bool:
    """Return whether a name is public (does not start with an underscore).

    Args:
        name: The identifier to test.

    Returns:
        True if the name is public.
    """
    return not name.startswith("_")


def _check_def(node: FuncNode, path: str, out: List[Violation]) -> None:
    """Check one public function/method for docstring and type-hint compliance.

    Args:
        node: Function or method definition node.
        path: Source file path (for reporting).
        out: Accumulator that receives any violations found.

    Returns:
        None. Violations are appended to ``out``.
    """
    doc = ast.get_docstring(node)
    if not doc:
        out.append((path, node.lineno, f"'{node.name}': missing docstring"))
    else:
        low = doc.lower()
        if _non_self_args(node) and "args:" not in low:
            out.append((path, node.lineno, f"'{node.name}': docstring missing 'Args:' section"))
        if _has_non_none_return(node) and "returns:" not in low and "yields:" not in low:
            out.append(
                (
                    path,
                    node.lineno,
                    f"'{node.name}': docstring missing a 'Returns:'/'Yields:' section",
                )
            )
    for arg in _non_self_args(node):
        if arg.annotation is None:
            out.append(
                (path, node.lineno, f"'{node.name}': parameter '{arg.arg}' missing type hint")
            )
    if node.returns is None:
        out.append((path, node.lineno, f"'{node.name}': missing return type hint"))


def check_file(path: Path) -> List[Violation]:
    """Check a single Python source file against the enforced guideline rules.

    Args:
        path: Path to the ``.py`` file.

    Returns:
        A list of ``(path, line, message)`` violations (empty if compliant).
    """
    out: List[Violation] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [(str(path), exc.lineno or 0, f"syntax error: {exc.msg}")]

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _public(node.name):
            _check_def(node, str(path), out)
        elif isinstance(node, ast.ClassDef) and _public(node.name):
            if not ast.get_docstring(node):
                out.append((str(path), node.lineno, f"class '{node.name}': missing docstring"))
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and _public(item.name):
                    _check_def(item, str(path), out)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ):
            out.append((str(path), node.lineno, "print() call — use the logging module"))
        if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
            out.append((str(path), node.lineno, "wildcard 'import *' is not allowed"))

    seen_code = False
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if seen_code:
                out.append((str(path), node.lineno, "module-level import not at top of file"))
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        else:
            seen_code = True
    return out


def main() -> int:
    """Run the guideline gate over the requested paths and report violations.

    Returns:
        Process exit code: 0 if compliant, 1 if any violations were found.
    """
    parser = argparse.ArgumentParser(description="Developer-guidelines enforcement gate")
    parser.add_argument("--paths", nargs="+", default=["src"], help="Directories/files to check")
    args = parser.parse_args()

    files: List[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(f for f in p.rglob("*.py") if "__pycache__" not in f.parts))
        elif p.suffix == ".py":
            files.append(p)

    violations: List[Violation] = []
    for f in files:
        violations.extend(check_file(f))

    write = sys.stdout.write
    if violations:
        write("DEVELOPER GUIDELINES — VIOLATIONS\n")
        for path, line, msg in violations:
            write(f"  {path}:{line}: {msg}\n")
        write(f"\nFAIL: {len(violations)} violation(s) across {len(files)} file(s).\n")
        return 1
    write(f"PASS: developer guidelines clean ({len(files)} files checked).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
