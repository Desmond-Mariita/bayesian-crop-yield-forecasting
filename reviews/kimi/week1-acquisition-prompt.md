# Kimi manual-review prompt — week1-acquisition

The Kimi wrapper produced only a plan for this review (it stopped at plan-approval);
this is the same prompt the rest of the panel answered, for a manual Kimi run.

Usage: run from the repo root (CLI) or attach the `Read:` files (web UI); paste
everything below the line. Save Kimi's response **verbatim** to
`reviews/kimi/week1-acquisition.md` (replacing the plan-only file).

Note: the tree has moved slightly since the panel ran — `src/utils/config.py` now
supplies the API key (env → .env fallback), and the panel's findings are already fixed
(POWER transport-failure tests, source-agnostic errors, etc.). Kimi should review the
CURRENT files as attached.

---

Role: You are an independent senior reviewer with expertise in data engineering for ML, API client design, and Python code quality.

Context: `bayesian-crop-yield-forecasting` is a learning repo mirroring the governance of a production farm platform (CI-enforced invariants in docs/INVARIANTS.md, data cards, a graduation gate for curriculum stubs). This increment is Week 1 of the curriculum: the module `src/data/acquisition.py` graduated its two functions — `download_nass_yields` (USDA NASS Quick Stats county yields) and `download_weather_data` (NASA POWER daily agroclimatology; a deliberate curriculum decision over the stub's original NOAA/PRISM plan) — plus the LINV-010 notebook-EXECUTION gate (pytest --nbmake in tools/verify.py) and the centralised config lookup (src/utils/config.py, env first with .env fallback).

Task: Critically review this increment for correctness, test quality, graduation-mechanics soundness, and documentation accuracy.

MANDATORY OUTPUT-PERSISTENCE RULE: this review must end up on disk at `reviews/kimi/week1-acquisition.md`.
- If you have file-system access, WRITE your full review to that path yourself and say so.
- If you do not, your ENTIRE response must be exactly the final review document in Markdown — no preamble, no closing chatter, nothing that cannot be saved verbatim to that file.

Read:
- src/data/acquisition.py
- src/utils/config.py
- tests/unit/test_acquisition.py
- tests/unit/test_weather_acquisition.py
- tests/unit/test_config.py
- tests/integration/test_acquisition_smoke.py
- tests/unit/test_stub_contracts.py
- src/curriculum_ledger.py
- tools/check_notebooks.py
- tools/verify.py
- pyproject.toml
- notebooks/data/acquisition.ipynb
- notebooks/TEMPLATE.ipynb
- data/samples/nass_quickstats_sample.json
- data/samples/nasa_power_sample.json
- docs/data_cards/DC-usda-nass-quickstats.md
- docs/data_cards/DC-nasapower-weather.md
- docs/INVARIANTS.md
- README.md

Checks (address each explicitly; if a check is clean, say so):
1. Acquisition correctness: NASS URL filters (survey-vs-census, year__GE) and POWER URL (parameters/community/date window); error payloads mapped to ConnectionError; "1,234" comma parsing; "(D)" suppression → NaN; POWER -999 fill → NaN; validation-before-network in download_weather_data (coordinates, POWER 1981 data start, year ordering); data_source tagging on every row; API-key hygiene (env/.env via src/utils/config.py, never logged).
2. Test quality: do the tests pin real behaviour (including both transport failure paths through the fake HTTP layer, for BOTH entry points) or mirror the implementation? Any untested branch that matters? Are all tests genuinely offline?
3. Graduation mechanics: with both names in IMPLEMENTED, the contract engine calls them with dummy args (floats 0.5, ints 2, no env vars, cwd = repo root). Confirm neither call can reach the network (NASS: required-key lookup raises first; POWER: year_start=2 fails validation first) and that the validation ordering is load-bearing, documented, and tested.
4. Notebook + execution gate: notebooks-execute wiring in verify.py (hard gate, --no-cov, deferred only when notebooks/ is empty); the repo-root bootstrap cell; getsource rule and offline rule honoured.
5. Data cards: accurate against the code (parameters, units, limitations, tags, date ranges)?
6. Cross-cutting: INVARIANTS/README claims vs actual gates; anything that breaks at the third graduation or as notebooks multiply.

Output format:
- Title line: `# week1-acquisition — Kimi review`
- Verdict: APPROVE / APPROVE-WITH-CHANGES / REQUEST-CHANGES, with 2-3 sentence rationale.
- Findings: numbered, each with Severity (Blocker/Major/Minor/Nit), exact file + line/clause, and a concrete recommended change.
- Answers to checks 1-6, explicitly.

Rules: use only the attached files; cite the exact file and line/clause for every finding; do not invent behaviour — if unsure, say so; if a check is clean, say so explicitly.
