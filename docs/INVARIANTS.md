# Project Invariants — bayesian-crop-yield-forecasting

**Version:** 1.0
**Status:** AUTHORITATIVE

Adapted in miniature from `keragita-farm-intelligence/docs/INVARIANTS.md` (the production
platform this repo trains for). These invariants MUST hold across all phases. A review
finding that cites an invariant violation is a blocker.

**Enforcement legend — read the column honestly:** *automated gate* = a named tool runs
in `tools/verify.py` + CI and blocks on violation (LINV-005, LINV-010 existence,
LINV-003 convergence checks via unit-tested `src/xai/gates.py`); *tests* = enforced only
as far as the test suite exercises it (LINV-001/002/008); *review* = human/agent review,
no automation yet (LINV-004/006/007/009 in part). Rows state which applies; aspiration
must never be dressed as CI.

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| LINV-001 | **XAI is first-class.** Every model exposes `explain_or_reject()` returning an `ExplanationCard` or a `RejectionCard` — never a bare point estimate, never an exception, never `None`. | `src/xai/` base contract; unit tests |
| LINV-002 | **RejectionCard is a first-class output.** Below-gate or low-confidence predictions are withheld with a structured `RejectionCard`, not forced through with a warning. | `src/xai/gates.py`; unit tests |
| LINV-003 | **Evidence gates before inference.** Each Bayesian milestone model declares an evidence gate (data thresholds) and a convergence gate (R-hat < 1.01, bulk/tail ESS > 400, 0 divergences) and may not be claimed "done" until both pass. | `src/xai/gates.py`; milestone checklists |
| LINV-004 | **Missing data is a model input, not a removed row.** Absence indicators are explicit features; silent row deletion or silent imputation is a violation. | review + Phase-2 milestone checklists (no automated gate yet — aspiration until the preprocessing modules graduate with indicator tests) |
| LINV-005 | **Every dataset has a data card** (source, method, resolution, date range, known limitations, intended use) before any code consumes it. Every shipped model artifact has a model card with `prior_justification` and convergence diagnostics. | Automated gate for card *schema* (`tools/check_data_cards.py` in `tools/verify.py` + CI); the dataset↔card *linkage* ("before any code consumes it") is review-enforced — the checker cannot know which datasets code touches |
| LINV-006 | **Wide priors until data justifies otherwise.** No tight priors on thin data; priors are documented and justified in the model card. | model-card review (no automated gate yet — a `prior_justification` schema check arrives with the model-card checker in Phase 2) |
| LINV-007 | **Domain constants carry provenance.** Every domain number (yield band, threshold, season window) lives in config with a `basis`/reference field — no magic numbers in code. | Review only for YAML/config provenance (`tools/check_guidelines.py` scans Python under `src/` and does not check config files); guidelines doc sets the norm |
| LINV-008 | **Determinism.** All stochastic code takes an explicit seed, logs it, and reproduces results bit-for-bit under the same seed. | unit tests; `docs/DEVELOPER_GUIDELINES.txt` §5 |
| LINV-009 | **Evidence before claims.** No task is "done" without a saved, timestamped verification report (`reports/verification/`) or evidence artifact under `reports/`. | Process/evidence gate: `tools/verify.py` produces the artifact; whether a task counts as "done" is review policy (CLAUDE.md), not machine-checkable |
| LINV-010 | **Every graduated curriculum module ships a companion notebook** at the mirrored path under `notebooks/` (e.g. `src/statistics/descriptive.py` → `notebooks/statistics/descriptive.ipynb`), following `notebooks/TEMPLATE.ipynb`: motivation, mathematics (LaTeX), the shipped source displayed via `inspect.getsource` (never a pasted copy — copies drift), a seeded worked example, pitfalls. Graduation = implementation + real unit tests + companion notebook, same week. *Infrastructure modules* = modules outside the curriculum stub ledger (currently `src/xai`); they are exempt unless opted into the checker's `EXTRA_MODULES`. | **CI enforces**: notebook existence at the mirrored path AND a dedicated test reference (outside the contract suites) for every graduated name (`tools/check_notebooks.py` in `tools/verify.py` + CI; graduation ledger = `IMPLEMENTED` in `src/curriculum_ledger.py`, imported by both the contract tests and the gate). A graduated name that still raises `NotImplementedError` fails the contract suite. Notebook content structure and the `getsource` rule are enforced by review; notebook *execution* (nbmake) is a planned gate that activates with the first companion notebook. |

## Violation procedure

1. Any reviewer (internal subagent or external backend) citing an invariant records it as
   a Blocker.
2. Work does not merge past a Blocker; the fix is verified by `tools/verify.py` (PASS).
3. Changing an invariant itself requires Desmond's explicit approval, logged in
   `research_log.md`.
