# Kimi manual-review prompt — governance-scaffold

Usage (manual, since the Kimi wrapper hangs on the Moonshot endpoint):
- **Kimi CLI / agentic:** run from the repo root and paste everything below the line.
- **Kimi web UI:** paste everything below the line and attach every file in the `Read:` list.
- Save Kimi's response **verbatim** to `reviews/kimi/governance-scaffold.md` (the prompt
  instructs Kimi to make that trivial). A review that is not saved to disk does not count.

---

Role: You are an independent senior reviewer with expertise in production ML systems, Bayesian statistics education, and Python code quality.

Context: `bayesian-crop-yield-forecasting` is a learning repo (Feb–Dec programme) whose charter is "derive every algorithm by hand in NumPy first, then rebuild each Bayesian milestone in PyMC/ArviZ and compare posteriors". It deliberately mirrors, in miniature, the governance of a production farm platform (keragita-farm-intelligence): CI-enforced invariants, an XAI card contract, data cards, evidence gates. Everything under `src/` except `src/xai` is curriculum stubs that raise NotImplementedError until their week arrives; `src/xai` is the first real code.

Task: Critically review the repo's governance scaffolding and curriculum for correctness, test quality, enforceability, and coherence.

MANDATORY OUTPUT-PERSISTENCE RULE: this review must end up on disk at `reviews/kimi/governance-scaffold.md`.
- If you have file-system access, WRITE your full review to that path yourself and say so.
- If you do not, your ENTIRE response must be exactly the final review document in Markdown — no preamble, no closing chatter, nothing that cannot be saved verbatim to that file.

Read:
- README.md
- research_log.md
- docs/INVARIANTS.md
- docs/learning-resources.md
- docs/DEVELOPER_GUIDELINES.txt
- src/xai/__init__.py
- src/xai/cards.py
- src/xai/gates.py
- src/xai/base.py
- tests/unit/test_xai_cards.py
- tests/unit/test_xai_gates.py
- tests/unit/test_stub_contracts.py
- tests/unit/test_stub_private_branches.py
- tests/integration/test_xai_smoke.py
- tools/verify.py
- tools/check_guidelines.py
- tools/check_data_cards.py
- tools/check_notebooks.py
- .github/workflows/ci.yml
- notebooks/TEMPLATE.ipynb
- config/crops/kilifi_crops.yaml
- docs/data_cards/DC-usda-nass-quickstats.md
- docs/data_cards/DC-kalro-kilifi-crops.md

Checks (address each explicitly; if a check is clean, say so):
1. src/xai correctness: card validation semantics (confidence bounds, empty-field checks, enum-member validation, deep-freeze of payloads and requirement tuples), EvidenceGate >= semantics and absent-key handling, evaluate_convergence strict boundaries (r_hat < 1.01, ess > 400, divergences == 0 — boundary values must fail), the ABC contract.
2. Test quality: do the unit/integration tests pin behaviour or mirror the implementation? Is the stub-contract engine (dynamic discovery + pinned EXPECTED_SURFACE manifest + IMPLEMENTED graduation ledger) sound — can it silently mis-discover, silently pass, or break when the first stub is implemented? Is asserting NotImplementedError for coverage an honest use of a 90% coverage gate?
3. Gate tools: check_data_cards.py restricted-frontmatter parser edge cases (colons in URLs, inline comments, empty list items); check_notebooks.py AST ledger-reading design (coupling a CI tool to a test-file constant); verify.py binary verdict logic; ci.yml calling verify.py as single source of truth.
4. Governance coherence: are the 10 invariants in docs/INVARIANTS.md enforceable exactly as their Enforcement column claims (automated gate vs tests vs review)? Any aspiration dressed as enforcement?
5. Curriculum: is the research_log.md milestone plan coherent with the charter and realistic (week counts, evidence gates, NumPy → PyMC loop)? Does learning-resources.md match the milestones?
6. Config/data: kilifi_crops.yaml structural validity and provenance completeness; the two data cards against the checker's required schema; inconsistencies between cards and the code/docs that cite them.
7. Cross-cutting: contradictions between README, INVARIANTS, research_log, and the tools; anything that will break the first time a stub actually graduates (implementation + real tests + IMPLEMENTED ledger entry + companion notebook).

Output format:
- Title line: `# governance-scaffold — Kimi review`
- Verdict: APPROVE / APPROVE-WITH-CHANGES / REQUEST-CHANGES, with 2-3 sentence rationale.
- Findings: numbered, each with Severity (Blocker/Major/Minor/Nit), exact file + line/clause, and a concrete recommended change.
- Answers to checks 1-7, explicitly.

Rules: use only the attached files; cite the exact file and line/clause for every finding; do not invent behaviour — if unsure, say so; if a check is clean, say so explicitly; a single "no findings" is not sign-off — state what you checked.
