# Self-audit: agent-written code vs docs/DEVELOPER_GUIDELINES.txt

**Date:** 2026-07-08
**Scope:** all Python written by the agent to date — `src/xai/` (cards, gates, base),
`src/curriculum_ledger.py`, `src/data/acquisition.py` (both graduated functions),
`tools/check_data_cards.py`, `tools/check_notebooks.py`, `tools/verify.py`
modifications, and the test suites.
**Method:** `tools/check_guidelines.py` (mechanical subset) + targeted greps
(print/imports/path-concat/os.path/raises/RNG) + clause-by-clause manual reading.

## Verdict: compliant, with 3 documented deviations and 2 notes

## Clause-by-clause

| Clause | Status | Evidence |
|---|---|---|
| §3 Google docstrings (Args/Returns) + PEP 484 hints everywhere | **PASS** | `check_guidelines.py`: clean, 34 files |
| §3 `Raises:` documented | **PASS** | every raising function documents it (cards 4, acquisition 5, tools 2; gates has no raises) |
| §3 Math from scratch / LaTeX above formulas | **N/A (yet)** | no formulas implemented by the agent; `notebooks/TEMPLATE.ipynb` §2 and the guidelines bind future math weeks |
| §3 Small, testable functions with reasoning comments | **PASS** | largest function ~45 lines (`download_weather_data`, mostly validation); load-bearing decisions carry why-comments (fail-closed warning, strict boundaries, validation-before-network) |
| §3 Invariants via assert or unit tests | **PASS** | 114 tests; boundary/immutability/contract invariants pinned; one production `assert` (list-shape, check_data_cards) |
| §4 Imports at top, no unused, no wildcard | **PASS** | checker + flake8 clean. *Note 1:* multi-name `from x import (a, b)` is used — read as "one import statement per line" (black/isort convention, accepted by the checker) |
| §4 pathlib only | **PASS** | no `os.path`, no string path concatenation (grep: none) |
| §4 No magic numbers; constants at top | **PASS** | thresholds/limits/timeouts/tags all named constants. *Note 2:* `RejectionCard.confidence=0.0` default and POWER date literals `0101`/`1231` are inline — semantic literals, arguably fine, could be constants |
| §4 Config centralized in `configs/` + `src/utils/config.py` with `.env` | **DEVIATION 1** | neither exists; `NASS_API_KEY` is read directly from `os.environ` (tested). The guideline itself is stale (says `configs/`; repo uses `config/` — also flagged by Codex r4). Proposed: create `src/utils/config.py` when a second env/config consumer appears; correcting the guideline text is Desmond's call |
| §4 logging not print | **PASS** | loggers in `acquisition`/`gates`; zero `print(` calls in agent code. CLI tools write their report to `sys.stdout.write` by design (pre-existing `verify.py` convention — the report *is* the output) |
| §5 Every new module: ≥1 unit + 1 integration test | **PASS for src, DEVIATION 2 for tools** | `src/xai` and `acquisition`: unit + integration suites. `src/curriculum_ledger.py`: no standalone file, but its content is directly asserted by `test_implemented_ledger_names_are_discovered` and it is import-covered. **`tools/*.py` have no pytest suites** — mitigation: they execute on every `verify.py`/CI run (smoke), and their failure paths were manually exercised with saved evidence during development; this follows the pre-existing convention (`check_guidelines.py` predates the agent and has no tests either). Proposed follow-up: unit tests for `parse_frontmatter`/`validate_card`/`search_token` — the three pure functions worth locking |
| §5 Fixed, logged seeds | **PASS** | agent src code uses no RNG (acquisition deterministic); tests use `default_rng(SEED)`, SEED=42, recorded in the smoke card's `technical_detail` |
| §5 Artifacts under `reports/` with timestamps | **PASS** | every verification run + analysis docs timestamped there |
| §6 Feature branches, rebase-then-merge, doc parity | **PASS** | every change on a `feat/`/`fix/` branch, merged `--no-ff` after verify PASS; README/INVARIANTS updated in the same commits |

## Deviations summary (ranked)

1. **No `src/utils/config.py` / `.env` layer** (§4) — acceptable today (one env var, read directly, tested); build it when config consumers multiply. The guideline's `configs/` path is itself outdated.
2. **`tools/` checkers lack pytest suites** (§5) — smoke-covered by CI on every run; worth adding unit tests for the three pure parsing/matching functions.
3. **`curriculum_ledger` has no dedicated test file** (§5, borderline) — its single constant is asserted by the contract suite's ledger test; a dedicated file would be ceremony.

Notes 1–2 (import style interpretation; two semantic literals) require no action unless
Desmond wants stricter readings.
