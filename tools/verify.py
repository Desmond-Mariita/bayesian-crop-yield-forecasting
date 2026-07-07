#!/usr/bin/env python3
"""Verification harness for bayesian-crop-yield-forecasting — runs every quality gate and writes a report.

This is the single command an agent runs to VERIFY the repository (developer guidelines,
lint, format, type-check, tests + coverage). It writes a timestamped, human-reviewable
report to ``reports/verification/`` (Markdown + JSON) and exits non-zero if the overall
verdict is FAIL. Modelled on MedInsight's policing / phase-report harness (ADR-048): the
agent runs this and saves the report; the reviewer reads the report, not the raw run.

Verdict is PASS only when every HARD gate passes; a hard gate that is FAIL or whose tool is
UNAVAILABLE makes the verdict FAIL (halt-on-failure spirit). The coverage gate is deferred
until the first test exists, then enforces ``--cov-fail-under``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

COV_FAIL_UNDER: int = 90
DETAIL_CHAR_LIMIT: int = 4000
TEMPLATE_NOTEBOOK: str = "TEMPLATE.ipynb"


def _run(cmd: List[str], cwd: Path) -> Tuple[int, str]:
    """Run a subprocess and capture its combined output.

    Args:
        cmd: Command and arguments to execute.
        cwd: Working directory to run in.

    Returns:
        A ``(returncode, combined_output)`` tuple; returncode 127 if the tool is missing.
    """
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except FileNotFoundError:
        return 127, f"tool not found: {cmd[0]}"


def _git_state(root: Path) -> Tuple[str, bool]:
    """Return the current git short SHA and whether the tree is dirty.

    Args:
        root: Repository root.

    Returns:
        A ``(short_sha, is_dirty)`` tuple; ``("N/A", False)`` if git is unavailable.
    """
    rc, out = _run(["git", "rev-parse", "--short", "HEAD"], root)
    sha = out if rc == 0 else "N/A"
    rc, _ = _run(["git", "diff", "--quiet"], root)
    return sha, rc != 0


def _status(rc: int, out: str = "") -> str:
    """Map a tool return code and output to a check status string.

    Args:
        rc: Subprocess return code.
        out: Combined tool output (used to detect a missing ``python -m`` module).

    Returns:
        "UNAVAILABLE" (missing tool/module), "PASS" (0), or "FAIL" (anything else).
    """
    if rc == 127 or "No module named" in out:
        return "UNAVAILABLE"
    return "PASS" if rc == 0 else "FAIL"


def _tests_exist(root: Path) -> bool:
    """Return whether pytest can collect at least one test.

    Args:
        root: Repository root.

    Returns:
        True if tests are collectable (pytest exit code is not 5).
    """
    rc, _ = _run([sys.executable, "-m", "pytest", "--co", "-q"], root)
    return rc != 5


def run_checks(root: Path, src: str, tests: str) -> List[Dict[str, object]]:
    """Run all verification gates and collect their results.

    Args:
        root: Repository root.
        src: Source directory to check.
        tests: Tests directory.

    Returns:
        A list of check-result dicts (name, hard, status, detail).
    """
    checks: List[Dict[str, object]] = []

    rc, out = _run([sys.executable, "tools/check_guidelines.py", "--paths", src], root)
    checks.append(
        {"name": "developer-guidelines", "hard": True, "status": _status(rc, out), "detail": out}
    )

    rc, out = _run([sys.executable, "tools/check_data_cards.py"], root)
    checks.append({"name": "data-cards", "hard": True, "status": _status(rc, out), "detail": out})

    rc, out = _run([sys.executable, "tools/check_notebooks.py"], root)
    checks.append({"name": "notebooks", "hard": True, "status": _status(rc, out), "detail": out})

    # The template is authoring scaffolding, not a companion notebook: executing it
    # would couple CI to whatever demo API its placeholder cells import.
    companion_notebooks = [
        p for p in (root / "notebooks").rglob("*.ipynb") if p.name != TEMPLATE_NOTEBOOK
    ]
    if companion_notebooks:
        rc, out = _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--no-cov",
                "--nbmake",
                f"--ignore=notebooks/{TEMPLATE_NOTEBOOK}",
                "notebooks",
            ],
            root,
        )
        checks.append(
            {"name": "notebooks-execute", "hard": True, "status": _status(rc, out), "detail": out}
        )
    else:
        checks.append(
            {
                "name": "notebooks-execute",
                "hard": True,
                "status": "DEFERRED",
                "detail": "no companion notebooks yet — execution gate deferred until the first one",
            }
        )

    rc, out = _run([sys.executable, "-m", "flake8", src, tests], root)
    checks.append({"name": "flake8", "hard": True, "status": _status(rc, out), "detail": out})

    rc, out = _run(
        [sys.executable, "-m", "black", "--check", "--line-length", "100", src, tests], root
    )
    checks.append({"name": "black", "hard": True, "status": _status(rc, out), "detail": out})

    rc, out = _run([sys.executable, "-m", "mypy", src], root)
    checks.append({"name": "mypy", "hard": False, "status": _status(rc, out), "detail": out})

    if not _tests_exist(root):
        checks.append(
            {
                "name": "pytest+coverage",
                "hard": True,
                "status": "DEFERRED",
                "detail": "no tests collected yet — coverage gate deferred until the first test",
            }
        )
    else:
        rc, out = _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                f"--cov={src}",
                "--cov-report=term-missing",
                "--cov-report=xml",
                f"--cov-fail-under={COV_FAIL_UNDER}",
                tests,
            ],
            root,
        )
        checks.append(
            {"name": "pytest+coverage", "hard": True, "status": _status(rc, out), "detail": out}
        )

    return checks


def render_markdown(
    checks: List[Dict[str, object]], ts: str, sha: str, dirty: bool, verdict: str
) -> str:
    """Render the human-reviewable Markdown verification report.

    Args:
        checks: Collected check results.
        ts: UTC timestamp string.
        sha: Git short SHA.
        dirty: Whether the working tree is dirty.
        verdict: Overall verdict (PASS/FAIL).

    Returns:
        The report as a Markdown string.
    """
    lines = [
        "# Verification Report — bayesian-crop-yield-forecasting",
        "",
        f"- **Generated (UTC):** {ts}",
        f"- **Git:** {sha}{' (dirty)' if dirty else ''}",
        f"- **Coverage gate:** >= {COV_FAIL_UNDER}%",
        f"- **Verdict:** {verdict}",
        "",
        "| Check | Result | Note |",
        "|---|---|---|",
    ]
    for c in checks:
        name = c["name"] if c["hard"] else f"{c['name']} (advisory)"
        note = (
            "deferred"
            if c["status"] == "DEFERRED"
            else ("" if c["status"] == "PASS" else "see details")
        )
        lines.append(f"| {name} | {c['status']} | {note} |")
    lines.append("")
    for c in checks:
        if c["status"] not in {"PASS", "DEFERRED"} and c["detail"]:
            detail = str(c["detail"])
            if len(detail) > DETAIL_CHAR_LIMIT:
                detail = detail[:DETAIL_CHAR_LIMIT] + "\n...[truncated]"
            lines.append(f"## {c['name']} — {c['status']}\n```\n{detail}\n```\n")
    return "\n".join(lines) + "\n"


def main() -> int:
    """Run the verification harness, write the report, and return an exit code.

    Returns:
        0 if the overall verdict is PASS, 1 if FAIL.
    """
    parser = argparse.ArgumentParser(
        description="bayesian-crop-yield-forecasting verification harness"
    )
    parser.add_argument("--src", default="src", help="Source directory")
    parser.add_argument("--tests", default="tests", help="Tests directory")
    args = parser.parse_args()

    root = Path.cwd()
    ts = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    sha, dirty = _git_state(root)
    checks = run_checks(root, args.src, args.tests)

    # Binary verdict, as documented: a hard gate that FAILs or whose tool is
    # UNAVAILABLE both make the run FAIL (the table still shows which it was).
    hard_bad = [c for c in checks if c["hard"] and c["status"] in {"FAIL", "UNAVAILABLE"}]
    verdict = "FAIL" if hard_bad else "PASS"

    outdir = root / "reports" / "verification"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        "project": "bayesian-crop-yield-forecasting",
        "generated_utc": ts,
        "git_sha": sha,
        "git_dirty": dirty,
        "cov_fail_under": COV_FAIL_UNDER,
        "verdict": verdict,
        "checks": checks,
    }
    (outdir / f"{ts}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = render_markdown(checks, ts, sha, dirty, verdict)
    (outdir / f"{ts}.md").write_text(md, encoding="utf-8")
    (outdir / "latest.md").write_text(md, encoding="utf-8")

    write = sys.stdout.write
    write(md)
    write(f"\nReport saved: reports/verification/{ts}.md  (verdict: {verdict})\n")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
