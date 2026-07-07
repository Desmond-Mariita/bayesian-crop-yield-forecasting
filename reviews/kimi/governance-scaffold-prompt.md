# Kimi manual-review prompt — governance-scaffold (v2, tree as of 2026-07-08)

Usage — `scripts/kimi_review.sh --exec` now runs this headlessly (verified 2026-07-08: `--exec` auto-approves so Kimi writes the review to disk itself, no plan-approval stall). The manual paths below remain a fallback:
- **Kimi CLI / agentic:** run from the repo root and paste everything below the line.
- **Kimi web UI:** paste everything below the line and attach every file in the `Read:` list.
- Save Kimi's response **verbatim** to `reviews/kimi/governance-scaffold-r2.md`
  (NOT `governance-scaffold.md` — that holds the 2026-07-07 review). A review that is
  not saved to disk does not count.

---

Role: You are an independent senior reviewer with expertise in production ML systems, Bayesian statistics education, and Python code quality.

Context: `bayesian-crop-yield-forecasting` is a learning repo (Feb–Dec programme) whose charter is "derive every algorithm by hand in NumPy first, then rebuild each Bayesian milestone in PyMC/ArviZ and compare posteriors". It mirrors, in miniature, the governance of a production farm platform (keragita-farm-intelligence): CI-enforced invariants, an XAI card contract, data cards, evidence gates, and a graduation pipeline for curriculum stubs. Current state: `src/xai` (XAI contract), `src/curriculum_ledger.py` (graduation ledger), `src/utils/config.py` (env/.env lookup), and both functions of `src/data/acquisition.py` (Week-1 graduations: NASS Quick Stats yields, NASA POWER weather) are real code; everything else under `src/` is curriculum stubs raising NotImplementedError. This scaffold has been through five external review rounds; you are auditing the CURRENT state fresh — do not assume any prior review's findings.

Task: Critically review the repo's governance scaffolding, graduation machinery, and Week-1 code for correctness, test quality, enforceability, and coherence.

MANDATORY OUTPUT-PERSISTENCE RULE: this review must end up on disk at `reviews/kimi/governance-scaffold-r2.md`.
- If you have file-system access, WRITE your full review to that path yourself and say so.
- If you do not, your ENTIRE response must be exactly the final review document in Markdown — no preamble, no closing chatter, nothing that cannot be saved verbatim to that file.

Read:
- README.md
- research_log.md
- docs/INVARIANTS.md
- docs/DEVELOPER_GUIDELINES.txt
- src/xai/__init__.py
- src/xai/cards.py
- src/xai/gates.py
- src/xai/base.py
- src/curriculum_ledger.py
- src/utils/config.py
- src/data/acquisition.py
- tests/unit/test_xai_cards.py
- tests/unit/test_xai_gates.py
- tests/unit/test_stub_contracts.py
- tests/unit/test_stub_private_branches.py
- tests/unit/test_acquisition.py
- tests/unit/test_weather_acquisition.py
- tests/unit/test_config.py
- tests/unit/test_tools_checkers.py
- tests/unit/test_curriculum_ledger.py
- tests/integration/test_xai_smoke.py
- tests/integration/test_acquisition_smoke.py
- tools/verify.py
- tools/check_guidelines.py
- tools/check_data_cards.py
- tools/check_notebooks.py
- .github/workflows/ci.yml
- notebooks/TEMPLATE.ipynb
- notebooks/data/acquisition.ipynb
- config/crops/kilifi_crops.yaml
- data/samples/nass_quickstats_sample.json
- data/samples/nasa_power_sample.json
- docs/data_cards/README.md
- docs/data_cards/DC-usda-nass-quickstats.md
- docs/data_cards/DC-nasapower-weather.md
- docs/data_cards/DC-kalro-kilifi-crops.md

Checks (address each explicitly; if a check is clean, say so):
1. src/xai correctness: card validation (confidence bounds, empty fields, enum-member checks, recursive deep-freeze, missing_requirements coercion/validation), EvidenceGate >= semantics with absent-keys-as-zero PLUS the loud warning, evaluate_convergence strict boundaries (1.01 / 400 exactly must FAIL), the ABC contract.
2. Graduation machinery: ledger in src/curriculum_ledger.py imported by both consumers; contract test flips graduated names to must-NOT-raise; tools/check_notebooks.py demands companion notebook AND a dedicated test reference outside the contract suites; discovery pinned by the EXPECTED_SURFACE manifest. Can any step be bypassed? What breaks at the next graduation?
3. Week-1 code: NASS and POWER acquisition (URL filters, error mapping to ConnectionError, "(D)"/-999 → NaN, comma parsing, validation-before-network ordering — load-bearing for the contract engine — data_source tagging, key hygiene via src/utils/config.py with .env fallback).
4. Gate tools + CI: restricted frontmatter parser (now unit-tested); notebooks-execute gate (pytest --nbmake, hard, deferred only when notebooks/ is empty); verify.py binary verdict; CI running verify.py as single source of truth.
5. Test quality across the board: pinning vs mirroring; offline-ness; the tools/ledger/config suites added 2026-07-08.
6. Governance coherence: the 10 invariants' Enforcement column (legend: automated gate / tests / review) — any aspiration dressed as enforcement?
7. Cross-cutting: contradictions between README, INVARIANTS, research_log, data cards, and the tools; realism of the Phase 2 plan.

Output format:
- Title line: `# governance-scaffold — Kimi review r2`
- Verdict: APPROVE / APPROVE-WITH-CHANGES / REQUEST-CHANGES, with 2-3 sentence rationale.
- Findings: numbered, each with Severity (Blocker/Major/Minor/Nit), exact file + line/clause, and a concrete recommended change.
- Answers to checks 1-7, explicitly.

Rules: use only the attached files; cite the exact file and line/clause for every finding; do not invent behaviour — if unsure, say so; if a check is clean, say so explicitly; a single "no findings" is not sign-off — state what you checked.
