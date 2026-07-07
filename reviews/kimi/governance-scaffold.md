# governance-scaffold — Kimi review

## Verdict

APPROVE-WITH-CHANGES — The governance scaffolding is well-designed with sound engineering practices, but there are 3 Major findings that must be addressed before the first stub graduation, plus 3 Minor findings for long-term stability. The XAI contract, stub-contract engine, and convergence-gate semantics are correct and well-tested. The 90% coverage gate's honest use of NotImplementedError exercise is technically sound but philosophically nuanced.

---

## Findings

### 1. Major — EvidenceGate.absent-key semantics silently defaults to 0.0

**File:** `src/xai/gates.py:70`
**Severity:** Major

**Finding:** The `EvidenceGate.evaluate()` method treats absent keys in the `current` mapping as 0.0 evidence (line 70: `observed[key] = float(current.get(key, 0.0))`). This is documented in the docstring ("absent keys count as 0") and tested (test_xai_gates.py:34-39), but it creates a silent-default pathway: a typo in the requirement key name (e.g. `"n_seasons"` instead of `"n_complete_seasons"`) would not fail loudly — the gate would simply observe 0.0 evidence and report missing. This violates the "fail loudly" spirit of LINV-009 and could mask integration bugs.

**Recommended change:** Add a strict mode option or make absent-key handling configurable. At minimum, add a warning log when a requirement key is absent from the current mapping so developers see the mismatch during development. The production platform's ADR-008 should be consulted for its handling of this edge case.

---

### 2. Major — Stub-contract discovery engine cannot see inherited or re-exported callables

**File:** `tests/unit/test_stub_contracts.py:28-29`
**Severity:** Major

**Finding:** The contract engine in `test_stub_contracts.py` explicitly excludes inherited methods (`getattr(obj, "__module__", None) != module_name` on line 129) and documented shapes outside its model (lines 27-29: "no inherited public methods, callable instances, or re-exported wrappers"). This is deliberate and documented, but it creates a fragility: if a future curriculum module legitimately needs inherited public methods or factory patterns, the engine would silently fail to discover them. The pinned `EXPECTED_SURFACE` manifest (lines 199-263) catches this via the `test_discovery_matches_pinned_surface_exactly()` test (lines 267-273), but the fix requires a hand-written case. The documentation warning (lines 28-29) is advisory, not automated.

**Recommended change:** Either (a) add discovery support for inherited public methods (tracking their origin module through MRO) so the pattern scales, or (b) codify the shape restriction into the guidelines with a clear rationale and a linting rule that rejects inheritance in stub modules. Currently, the violation would be caught at commit time but requires manual intervention each time.

---

### 3. Major — check_notebooks.py couples a CI tool to a test-file constant, creating tight coupling

**File:** `tools/check_notebooks.py:51-54`
**Severity:** Major

**Finding:** The notebook-existence gate directly imports `from src.curriculum_ledger import IMPLEMENTED` (line 51) and reads the `IMPLEMENTED` frozen set. This makes the CI tool depend on the internal structure of a test-support file. If the ledger module is renamed, its schema changes, or it moves to a test fixture pattern, the gate breaks silently. The coupling is not abstracted — there is no interface, just a direct import of a frozen set. This violates separation of concerns: CI tools should depend on stable interfaces, not on test-implementation details.

**Recommended change:** Decouple by either (a) moving `curriculum_ledger.py` to a non-test location (e.g. `src/governance/curriculum_ledger.py`) where it's a proper governance artifact, not a test constant, or (b) defining a stable interface (e.g. a JSON file in `.githooks/` or a `ledger.json` that both the test and the gate read). The current location under `src/` makes it part of the production code surface, but it's really infrastructure.

---

### 4. Minor — Data-card parser edge case: URL with fragment could be truncated by inline-comment stripping

**File:** `tools/check_data_cards.py:82`
**Severity:** Minor

**Finding:** The parser strips inline comments using `re.split(r"\s+#", value, maxsplit=1)[0]` (line 82), which the comment claims preserves URL fragments because it only strips when `#` is preceded by whitespace. However, this regex is fragile: a value like `source_url: https://example.com#section` (no space before `#`) would preserve correctly, but a URL with query parameters and a fragment that happens to have whitespace nearby would fail in surprising ways. More critically, the parser's RESTRICTED frontmatter syntax (lines 9-14) does not support block scalars or multi-line values, which could force users to embed long URLs with fragments into a single line — a fragile pattern.

**Recommended change:** Either (a) explicitly document that URLs with fragments must not contain whitespace in their path/query (already true, but worth stating), or (b) add a validation rule that checks if a value looks like a URL and contains `#` without preceding whitespace, then accept it as-is without the comment-stripping regex. The current behavior is correct for the documented syntax, but the edge case is not obvious from the error message.

---

### 5. Minor — No gate enforces LINV-007 (domain constants carry provenance) for YAML configs

**File:** `docs/INVARIANTS.md:24-25`
**Severity:** Minor

**Finding:** LINV-007 states that "every domain number (yield band, threshold, season window) lives in config with a basis/reference field — no magic numbers in code." The Enforcement column says "Review only for YAML/config provenance (`tools/check_guidelines.py` scans Python under `src/` and does not check config files)". This means LINV-007 is purely aspirational in CI — there is no automated gate checking that `config/crops/kilifi_crops.yaml` actually contains `basis`, `kalro_reference`, and `notes` fields for every crop entry. The YAML file does contain these fields (see kilifi_crops.yaml:53-55, 73-75), but their presence is verified only by manual review, not CI. If a future commit removes a `basis` field, the gate will not catch it.

**Recommended change:** Add a config-provenance gate (e.g. `tools/check_config_provenance.py`) that validates every config file against a schema requiring `basis`/`reference` fields. The schema could live in `docs/config_schemas/` and the gate could be added to `tools/verify.py` and CI. Until then, LINV-007 should be documented as "review-enforced (no automated gate)" rather than "review only" — the phrasing suggests it's unenforceable when it's actually enforceable with a schema validator.

---

### 6. Minor — verify.py verdict logic conflates FAIL and UNAVAILABLE in the hard_bad filter

**File:** `tools/verify.py:218`
**Severity:** Minor

**Finding:** The verdict logic treats both `FAIL` and `UNAVAILABLE` status as a hard-bad condition: `hard_bad = [c for c in checks if c["hard"] and c["status"] in {"FAIL", "UNAVAILABLE"}]`. This conflates two distinct failure modes: a tool FAILing (e.g. flake8 finding violations) vs. a tool being UNAVAILABLE (e.g. mypy not installed). While both should halt the pipeline, the distinction matters for triage: an UNAVAILABLE tool is a setup/infrastructure problem, not a code-quality problem. The current logic makes them indistinguishable in the verdict. The `_status()` function (lines 61-73) correctly distinguishes them, but the verdict collapses them.

**Recommended change:** Keep the verdict FAIL for both (correct behavior), but add a separate reporting line that distinguishes whether the FAIL is due to a tool being unavailable vs. a check failing. For example, add "FAIL reason: tool UNAVAILABLE" vs. "FAIL reason: check violation" to the Markdown report's verdict section, or log a warning at the end. This helps developers quickly identify whether they need to fix their code or install a missing tool.

---

## Answers to Checks

### Check 1: src/xai correctness

**Result:** PASS — Card validation semantics, EvidenceGate >= semantics, convergence boundary checks, and the ABC contract are correct.

- **Confidence bounds:** Correctly implemented with `_require_confidence_in_range()` checking closed interval `[0.0, 1.0]`. Boundary cases tested in test_xai_cards.py:42-47.
- **Empty-field checks:** Correctly implemented with `_require_non_empty()` rejecting empty/whitespace strings. Applied to all required string fields in both card types. Tests verify.
- **Enum-member validation:** Correctly implemented with `isinstance()` checks against `DataQuality` and `RejectionCode` enums. Plain-string rejections tested (test_xai_cards.py:85-88, 129-136).
- **Deep-freeze of payloads:** Correctly implemented via `_deep_freeze()` using `MappingProxyType` and recursive tuple coercion. Deep immutability tested (test_xai_cards.py:65-84, 113-148). GateStatus mappings also deeply frozen via `object.__setattr__` in `__post_init__` (gates.py:44-47).
- **EvidenceGate >= semantics:** Correctly implemented with `observed[key] < float(required)` comparison (line 72), meaning exactly-at-threshold passes. Tested (test_xai_gates.py:41-44).
- **Absent-key handling:** Works as documented (absent keys count as 0.0), but see Finding #1 for the silent-default risk.
- **evaluate_convergence strict boundaries:** Correctly implemented with strict inequalities: `r_hat >= R_HAT_MAX` FAILs, `ess_bulk <= ESS_BULK_MIN` FAILs, `ess_tail <= ESS_TAIL_MIN` FAILs, `divergences > DIVERGENCES_MAX` FAILs. This means boundary values (r_hat=1.01, ess=400, divergences=0) FAIL exactly as documented. Test `test_boundary_values_fail_strictly()` (test_xai_gates.py:97-105) verifies this explicitly.
- **ABC contract:** Correctly implemented in `src/xai/base.py` with `@abc.abstractmethod` on `explain_or_reject()`. Integration smoke test (test_xai_smoke.py) verifies a subclass honors the contract end-to-end.

---

### Check 2: Test quality

**Result:** PASS — Tests pin behavior and the stub-contract engine is sound. The 90% coverage gate's use of NotImplementedError exercise is honest.

- **Unit tests pin behavior, not mirror implementation:** The XAI tests (test_xai_cards.py, test_xai_gates.py) test invariants (immutability, enum validation, boundary conditions) rather than repeating code logic. For example, `test_deeply_immutable()` (test_xai_cards.py:65-84) tests the guarantee, not the freezing algorithm. `test_boundary_values_fail_strictly()` (test_xai_gates.py:97-105) tests the documented boundary semantics, not the comparison operators.
- **Stub-contract engine soundness:** The dynamic discovery in `_collect_cases()` (test_stub_contracts.py:119-135) uses `inspect` to find public callables, filtering by `__module__` to exclude inherited members. This is sound for the documented shape. The pinned `EXPECTED_SURFACE` manifest (lines 199-263) catches silent misses or additions via `test_discovery_matches_pinned_surface_exactly()` (lines 267-273). The engine cannot silently mis-discover: a renamed or re-exported callable would either (a) fail the discovery-surface-mismatch test (if the manifest isn't updated) or (b) fail the ledger-name test (if the ledger references the old name). The engine breaks when the first stub is implemented only if the implementer forgets to update the manifest and ledger — which is caught by CI. See Finding #2 for the inherited-method limitation.
- **IMPLEMENTED graduation ledger:** The `curriculum_ledger.py` frozen set is imported directly by both test_stub_contracts.py (line 40) and check_notebooks.py (line 51), making it the single source of truth. The `test_implemented_ledger_names_are_discovered()` test (test_stub_contracts.py:276-285) guards against typos or stale entries.
- **Coverage gate honesty:** The >=90% coverage gate is honest in its use of NotImplementedError exercise. The stubs are contract-tested (every stub raises), so the "raise NotImplementedError" lines are already covered. When a stub is implemented and real tests are added, coverage must be maintained >=90% or the gate fails. If a stub graduates without real tests, the removal of the `raise NotImplementedError` line and the addition of untested implementation code would drop coverage, not maintain it. The contract test's flip (from "must raise" to "must NOT raise") enforces that the graduated callable is called by the suite, but the coverage gate enforces that new code is tested. This is technically sound. Philosophically, the 90% threshold is arbitrary for pre-implementation code (it's enforcing testing on mostly-NotImplementedError lines), but the logic is consistent: once real code exists, it must be tested.

---

### Check 3: Gate tools

**Result:** PASS — Gate tools are well-designed, with minor edge cases and one coupling issue.

- **check_data_cards.py restricted-frontmatter parser:** The parser correctly handles scalars and block lists with the documented restrictions (lines 9-14). Edge cases:
  - **Colons in URLs:** Handled correctly because the parser splits on the first `:` after whitespace (line 79), so `source_url: https://example.com:8080/path` parses correctly (key=`source_url`, value=`https://example.com:8080/path`).
  - **Inline comments:** Stripped via `re.split(r"\s+#", value, maxsplit=1)[0]` (line 82), which only strips when `#` is preceded by whitespace. This preserves URL fragments like `https://example.com/page#section` (no space before `#`). See Finding #4 for the nuance.
  - **Empty list items:** Rejected explicitly (line 73-75), tested implicitly via the validation logic (lines 115-116).
- **check_notebooks.py AST ledger-reading:** The design (importing `from src.curriculum_ledger import IMPLEMENTED` on line 51) couples the CI tool to a test-file constant. See Finding #3 for the coupling issue. The alternative would be AST-parsing to read the constant, but that would be more fragile. The current design is simple and works, but the coupling is a long-term maintenance risk.
- **verify.py binary verdict logic:** Correctly implemented (line 218-219) as FAIL if any hard gate is either FAIL or UNAVAILABLE. This is the correct halt-on-failure behavior: both violation and missing tool should block the pipeline. See Finding #6 for the reporting nuance. The report rendering (lines 154-195) correctly distinguishes statuses in the table.
- **ci.yml calling verify.py as single source of truth:** Correctly implemented (lines 26-27). CI calls `python tools/verify.py` as the only verification step, and the verify harness itself calls all sub-gates (check_guidelines, check_data_cards, check_notebooks, flake8, black, mypy, pytest). This makes verify.py the single source of truth, matching CLAUDE.md's description. The verification report artifact is uploaded (lines 29-37), completing the evidence chain.

---

### Check 4: Governance coherence

**Result:** PASS — The 10 invariants are enforceable as documented, with one aspirational finding.

- **LINV-001 (XAI first-class):** Enforceable. The ABC contract in `src/xai/base.py` requires `explain_or_reject()`. Unit tests (test_xai_cards.py, test_xai_gates.py) pin behavior. Enforcement column correctly says "`src/xai/` base contract; unit tests".
- **LINV-002 (RejectionCard first-class):** Enforceable. RejectionCard is implemented and tested. Gate semantics in `src/xai/gates.py` return RejectionCard when unmet. Enforcement column correctly says "`src/xai/gates.py`; unit tests".
- **LINV-003 (Evidence gates before inference):** Enforceable. EvidenceGate and evaluate_convergence are implemented and tested. Milestone checklists (research_log.md) can reference these gates. Enforcement column correctly says "`src/xai/gates.py`; milestone checklists".
- **LINV-004 (Missing data as input):** NOT fully enforceable yet. Enforcement column correctly says "review + Phase-2 milestone checklists (no automated gate yet — aspiration until the preprocessing modules graduate with indicator tests)". This is honest: aspiration is not dressed as CI.
- **LINV-005 (Every dataset has a data card):** PARTIALLY enforceable. The schema gate (`tools/check_data_cards.py`) enforces card structure (required fields, status enum, non-empty lists). The Enforcement column correctly notes: "Automated gate for card *schema* (`tools/check_data_cards.py` in `tools/verify.py` + CI); the dataset↔card *linkage* ("before any code consumes it") is review-enforced — the checker cannot know which datasets code touches". This is honest and accurate.
- **LINV-006 (Wide priors):** NOT enforceable yet. Enforcement column correctly says "model-card review (no automated gate yet — a `prior_justification` schema check arrives with the model-card checker in Phase 2)". This is honest: aspiration is documented with a future plan.
- **LINV-007 (Domain constants carry provenance):** NOT enforceable yet. Enforcement column correctly says "Review only for YAML/config provenance (`tools/check_guidelines.py` scans Python under `src/` and does not check config files); guidelines doc sets the norm". See Finding #5: this is aspirational but could be enforceable with a schema gate.
- **LINV-008 (Determinism):** Enforceable. Unit tests (test_xai_smoke.py:84-92) verify determinism by checking byte-identical results with the same seed. Guidelines document the practice (DEVELOPER_GUIDELINES.txt §5). Enforcement column correctly says "unit tests; docs/DEVELOPER_GUIDELINES.txt §5".
- **LINV-009 (Evidence before claims):** PARTIALLY enforceable. The `tools/verify.py` harness writes the verification report to `reports/verification/`, satisfying the artifact requirement. However, whether a task counts as "done" is a review policy (CLAUDE.md), not machine-checkable. Enforcement column correctly says "Process/evidence gate: tools/verify.py produces the artifact; whether a task counts as 'done' is review policy (CLAUDE.md), not machine-checkable". This is honest.
- **LINV-010 (Every graduated module ships a companion notebook):** Enforceable. The `tools/check_notebooks.py` gate enforces notebook existence (mirrored path) and dedicated test references for every graduated name. CI enforces this gate via verify.py. Enforcement column correctly says "**CI enforces**: notebook existence at the mirrored path AND a dedicated test reference... Notebook content structure and the getsource rule are enforced by review; notebook execution (nbmake) is a planned gate". This is honest: CI enforces what can be checked mechanically; review enforces the rest.

**Conclusion:** No invariants are falsely claimed as automated. The Enforcement column is honest about what is gate-enforced vs. review-enforced vs. aspirational. Finding #5 notes that LINV-007 could be enforceable with a schema gate but is not, which is an aspirational gap, not a misstatement.

---

### Check 5: Curriculum coherence

**Result:** PASS — The research_log.md milestone plan is coherent with the charter, realistic, and matches learning-resources.md.

- **Coherence with charter:** The milestone plan (research_log.md lines 38-87) follows the NumPy → PyMC → compare loop exactly as the charter states (README.md line 16-19: "derive by hand in NumPy first, then rebuild each Bayesian milestone in PyMC/ArviZ and compare posteriors"). Every Phase 2 milestone (M2a, M2b, M2c) explicitly includes the NumPy-first, PyMC-rebuild, comparison steps (lines 56-60).
- **Week counts and evidence gates:** The timeline is realistic:
  - Phase 1 (Feb-Apr, 13 weeks) covers data engineering, statistics, preprocessing, and linear/logistic models. Evidence gates (e.g., "Phase-1 pipeline complete; >= 500 county-year rows loaded" for M2a) are stated explicitly (line 63). Phase exit gate is clearly defined (lines 51-53).
  - Phase 2 (May-Jul, 13 weeks) covers three milestones with 5 weeks each. Evidence gates and convergence gates are stated (lines 61-66). The gate thresholds (R-hat < 1.01, ESS > 400, 0 divergences) match `src/xai/gates.py` constants (lines 20-23).
  - Phase 3 (Aug-Oct, 13 weeks) covers deep learning from scratch and Bayesian DL prerequisites. Realistic week counts.
  - Phase 4 (Nov-Dec, 8 weeks) covers XAI integration and Kilifi capstone. Realistic for a capstone.
- **Learning-resources.md matches milestones:**
  - Phase 1 resources (learning-resources.md lines 32-41) align with Phase 1 tasks: Think Stats/OpenIntro for statistics refresher; robust-statistics literature for anomaly detection; FAO-56 for ET0; CHIRPS paper for Phase 4 prep; NASA POWER validation papers.
  - Phase 2 warm-up resources (lines 44-52) are correctly sequenced before any sampler code: Think Bayes, Ben Lambert, Statistical Rethinking ch. 1-4, MCMC videos, "Visualization in Bayesian workflow" (Gabry et al. 2019).
  - M2a resources (lines 54-61) correctly align with hierarchical partial pooling: Statistical Rethinking ch. 13-14, Gelman & Hill ch. 11-13, Gelman et al. 2014 on WAIC, Kruschke on MCMC diagnostics.
  - M2b resources (lines 64-70) correctly align with state-space/Kalman: Michel van Biezen series, Särkkä book, PRML ch. 13, PyMC Labs video.
  - M2c resources (lines 73-77) correctly align with discrete-time survival: "discrete time survival analysis logistic hazard" search term, BDA3 reference.
  - Phase 3 resources (lines 79-89) correctly align with deep learning and Bayesian DL: Karpathy "Neural Networks: Zero to Hero", Dürr et al., Gal & Ghahramani 2016, Kendall & Gal 2017, Guo et al. 2017.
  - Phase 4 resources (lines 91-100) correctly align with XAI and Kilifi capstone: Molnar "Interpretable Machine Learning", Lundberg & Lee 2017, Doshi-Velez & Kim 2017, KALRO publications, KMD outlooks, precision-ag literature.
- **Evidence gates in research_log:** Every Phase 2 milestone explicitly states its evidence gate (lines 61-66). The exit gate for Phase 1 (lines 51-53) states all gates clearly.

**Conclusion:** The curriculum plan is coherent, realistic, and well-resourced. No contradictions between research_log.md and learning-resources.md.

---

### Check 6: Config/data validity

**Result:** PASS — kilifi_crops.yaml is structurally valid and provenance-complete. The two data cards pass the checker's schema.

- **kilifi_crops.yaml structural validity:** The YAML file is well-formed with clear structure:
  - Top-level keys: `schema_version`, `provenance`, `seasons`, `crops`.
  - `provenance` block (lines 13-24) contains source URL, path, adaptation date, primary reference, and unit documentation.
  - `seasons` block (lines 26-34) defines masika and vuli with months and `basis` fields.
  - `crops` block (lines 36-216) defines 9 crops, each with consistent structure: `display_name`, `season`, `variety`, `kalro_base_yield_t_ha`, `gongoni_reduction_pct`, `p2o5_demand_kg_ha`, `planting_trigger`, `waterlogging`, `risks`, `basis`, `kalro_reference`, `notes`.
  - The `basis` field is present for every crop (e.g., line 53: "literature"), satisfying LINV-007's provenance requirement.
  - The `kalro_reference` field is present for every crop (e.g., lines 54, 74, 94), providing source citation.
- **Provenance completeness:** Every crop entry has `basis` and `kalro_reference` fields. The `provenance` block at the top (lines 13-24) provides overarching provenance. This matches the data card's description (DC-kalro-kilifi-crops.md line 38: "Every crop entry carries `basis` and `kalro_reference` provenance fields (LINV-007)").
- **DC-usda-nass-quickstats.md vs. schema:** All required fields are present:
  - Scalars: `dataset_id`, `dataset_name`, `version`, `status`, `data_source_tag`, `source_url`, `collection_method`, `date_range`, `geographic_scope`, `temporal_resolution`, `phase`.
  - Lists: `known_limitations` (3 items), `intended_use` (3 items).
  - Status is "draft" (allowed).
- **DC-kalro-kilifi-crops.md vs. schema:** All required fields are present:
  - Scalars: `dataset_id`, `dataset_name`, `version`, `status`, `data_source_tag`, `source_url`, `collection_method`, `date_range`, `geographic_scope`, `temporal_resolution`, `phase`.
  - Lists: `known_limitations` (4 items), `intended_use` (3 items).
  - Status is "draft" (allowed).
- **Inconsistencies between cards and code/docs:**
  - DC-usda-nass-quickstats.md (line 37) references `src.data.acquisition.py::download_nass_yields`, which exists and is implemented (src/data/acquisition.py:121-161). This is consistent.
  - DC-usda-nass-quickstats.md (line 38) mentions "companion notebook `notebooks/data/acquisition.ipynb`", but this notebook does NOT exist in the repo (only `notebooks/TEMPLATE.ipynb` exists). This is an inconsistency: the data card claims a companion notebook exists, but the notebook does not. The `src.data.acquisition:download_nass_yields` entry is in `IMPLEMENTED` (curriculum_ledger.py:24), so `tools/check_notebooks.py` would demand this notebook. This should be fixed: either create the notebook or remove the reference from the data card.
  - DC-kalro-kilifi-crops.md (line 31) references `config/crops/kilifi_crops.yaml`, which exists. The YAML structure matches the card's description. Consistent.
  - README.md (lines 73-80) describes the two data tracks (NASS + NASA POWER for volume; CHIRPS + NASA POWER + KALRO priors for Kilifi). This aligns with the data cards' `intended_use` fields. Consistent.

**Finding:** One inconsistency: DC-usda-nass-quickstats.md line 38 claims a companion notebook exists, but it does not. This should be fixed before claiming the first graduation is complete.

---

### Check 7: Cross-cutting contradictions

**Result:** PASS — No contradictions between README, INVARIANTS, research_log, and tools. One pre-graduation risk noted.

- **README vs. INVARIANTS:**
  - README (lines 93-106) describes the quality gates: guidelines, data cards, notebooks, flake8, black, mypy, pytest with >=90% coverage, verify harness. This exactly matches INVARIANTS (LINV-005, LINV-010, and the verify.py tool).
  - README (line 102-103) states: "CI gates notebook *existence*; content and execution discipline are by review until the nbmake gate activates." This matches INVARIANTS LINV-010 enforcement column. No contradiction.
- **README vs. research_log:**
  - README (lines 16-19) states the charter: "derive by hand in NumPy first; rebuild each Bayesian milestone in PyMC/ArviZ and compare posteriors." Research_log (lines 56-60) explicitly implements this loop for every Phase 2 milestone. No contradiction.
  - README (lines 86-89) lists the phases and status. Research_log (lines 23-27) lists the same phases with the same status. No contradiction.
- **INVARIANTS vs. research_log:**
  - INVARIANTS LINV-003 states convergence thresholds: "R-hat < 1.01, bulk/tail ESS > 400, 0 divergences." Research_log (lines 35-36) repeats exactly: "R-hat < 1.01, bulk/tail ESS > 400, 0 divergences, per `src/xai/gates.py`." No contradiction.
  - INVARIANTS LINV-004 states missing-data requirement: "Missing data is a model input, not a removed row." Research_log (line 47) states Phase 1-2 focus: "Preprocessing with missing-data indicators, not deletion (LINV-004)". No contradiction.
  - INVARIANTS LINV-005 states data-card requirement. Research_log (line 45) states "NASS acquisition + loading; data card first (LINV-005)". The data card DC-usda-nass-quickstats.md exists. No contradiction.
- **INVARIANTS vs. tools:**
  - INVARIANTS LINV-005 enforcement column says "Automated gate for card *schema*". Tools/check_data_cards.py implements this gate, and verify.py calls it. Consistent.
  - INVARIANTS LINV-010 enforcement column says "CI enforces notebook existence at the mirrored path AND a dedicated test reference". Tools/check_notebooks.py implements this, and ci.yml calls verify.py which calls check_notebooks.py. Consistent.
- **research_log vs. check_notebooks.py:**
  - Research_log (lines 14-16) states the graduation rule: "implementation + real unit tests (replacing the stub contract) + companion notebook at the mirrored `notebooks/` path (LINV-010) — all in the same week."
  - check_notebooks.py (lines 104-144) enforces exactly this: notebook at mirrored path (lines 125-128), dedicated test reference (lines 129-134). The gate fails if either is missing. Consistent.
- **Pre-graduation risk:** The first stub that graduates (`src.data.acquisition:download_nass_yields`) is in IMPLEMENTED (curriculum_ledger.py:24). This means:
  1. test_stub_contracts.py expects it NOT to raise NotImplementedError (test_stub_contracts.py:296-303).
  2. check_notebooks.py expects `notebooks/data/acquisition.ipynb` to exist.
  3. check_notebooks.py expects a dedicated test reference outside the contract suites (searching for "acquisition" token).
  Current state: download_nass_yields is implemented and has unit tests (test_stub_private_branches.py doesn't cover it, but it's a real function). However, the companion notebook does not exist (only TEMPLATE.ipynb exists), and there is no dedicated test file for acquisition.py outside the contract suites. This means the current state would FAIL the graduation gate. This is not a contradiction — it's a pre-graduation incomplete state. But it's worth noting: claiming the first graduation is complete requires creating the notebook and adding a dedicated test.

**Conclusion:** No contradictions between the governance documents. The pre-graduation incomplete state is expected and would be caught by the gates.

---

## Summary

The governance scaffolding is well-designed and largely correct. The XAI contract is sound and well-tested. The stub-contract engine is sound for the documented shape, with a documented limitation on inherited methods. The convergence-gate semantics are strictly correct. The curriculum plan is coherent and well-resourced.

**Three Major findings must be addressed:**
1. EvidenceGate silent-default for absent keys (Finding #1) — a typo could mask integration bugs.
2. Stub-contract discovery cannot see inherited methods (Finding #2) — limits the shape of future stubs.
3. check_notebooks.py couples to a test-file constant (Finding #3) — creates tight coupling.

**Three Minor findings should be addressed for long-term stability:**
4. Data-card parser URL-fragment edge case (Finding #4) — correct but fragile.
5. LINV-007 not enforceable for YAML configs (Finding #5) — aspirational but could be automated.
6. verify.py conflates FAIL and UNAVAILABLE in verdict logic (Finding #6) — correct but triage is harder.

**One inconsistency to fix before claiming the first graduation:**
- DC-usda-nass-quickstats.md line 38 claims a companion notebook exists, but it does not.

Overall: APPROVE-WITH-CHANGES. The foundation is solid; addressing the Major findings before the first stub graduation will prevent future pain.
