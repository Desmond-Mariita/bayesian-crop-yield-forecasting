# governance-scaffold — Kimi review

**Reviewer:** Independent senior reviewer (production ML, Bayesian statistics education, Python quality)  
**Date:** 2026-07-07  
**Scope:** Governance scaffolding, curriculum plan, XAI contract, gate tools, data/config provenance  
**Verdict:** APPROVE-WITH-CHANGES

The governance scaffolding is unusually rigorous for a learning repo. The enforcement columns in `docs/INVARIANTS.md` are refreshingly honest about what is automated versus what remains review-enforced, and the graduation mechanism (stub contract → `IMPLEMENTED` ledger → companion notebook gate) creates a genuine TDD nudge rather than theatre. The XAI contract (`src/xai/cards.py`, `gates.py`, `base.py`) is correctly implemented with strict boundary semantics, deep immutability, and comprehensive unit tests. The few issues found are architectural nits and one Major limitation of the global coverage gate that should be documented before Phase 2 scale-up.

---

## Findings

### Major

**1. Global coverage gate does not guarantee per-module test quality at graduation**  
*File:* `tests/unit/test_stub_contracts.py` (docstring, coverage note, lines 17–20)  
*Clause:* "Graduating a stub without real tests would drop coverage, not maintain it."  
*Issue:* The 90 % target in `tools/verify.py` is global. A small implementation (e.g. a 5-line closed-form linear-regression fitter) can graduate with only trivial tests and still leave the global average above 90 % if the rest of the codebase is well-covered by stub-contract tests. The gate therefore does not mechanically enforce the graduation rule "real unit tests" for every module.  
*Recommended change:* Add an explicit caveat to the docstring: "The global gate is a backstop, not a per-module guarantee; every graduated module must still have its own `test_<module>.py` file, verified by review." Consider adding a lightweight per-module smoke gate in Phase 2 (e.g. `pytest --co tests/unit/test_<module>.py` must collect ≥1 test for every name in `IMPLEMENTED`).

### Minor

**2. `check_data_cards.py` parser footgun with spaced hashes**  
*File:* `tools/check_data_cards.py`, lines 80–82  
*Clause:* `value = re.split(r"\s+#", value, maxsplit=1)[0]`  
*Issue:* The documented claim is "URLs with fragments survive" (line 13 docstring), but this only holds when `#` is not preceded by whitespace. A data-card author who writes `source_url: https://example.com/page #section` (with a space before the fragment) will silently have the fragment truncated. This is a footgun for authors unfamiliar with the restricted parser.  
*Recommended change:* Add a one-line warning to the data-card template or to `docs/data_cards/README.md`: "Do not put spaces before `#` in frontmatter values; the parser treats them as inline-comment starts."

**3. `check_notebooks.py` is coupled to the AST shape of a test file**  
*File:* `tools/check_notebooks.py`, lines 28–29, 37–74  
*Clause:* `LEDGER_PATH: Path = Path("tests/unit/test_stub_contracts.py")`  
*Issue:* The notebook gate reads the `IMPLEMENTED` frozenset via AST from the stub-contract test module. While both files document this coupling (`test_stub_contracts.py` line 23: "Keep it a literal frozenset(...) call"), it remains brittle. Renaming the test file, moving the ledger, or changing its assignment syntax will break CI's notebook gate.  
*Recommended change:* In Phase 2, extract `IMPLEMENTED` to a standalone module (e.g. `src/_curriculum_ledger.py`) that both `test_stub_contracts.py` and `check_notebooks.py` import. This removes the AST dependency entirely.

**4. RejectionCard snapshot test lives in the wrong class**  
*File:* `tests/unit/test_xai_cards.py`, lines 85–95  
*Clause:* `class TestExplanationCard:` contains `test_missing_requirements_list_is_snapshotted`  
*Issue:* The test builds a `RejectionCard` and asserts on `missing_requirements` tuple coercion, but it is nested inside `TestExplanationCard`. This is a pure organization issue; it does not affect correctness.  
*Recommended change:* Move the method into `class TestRejectionCard`.

### Nit

**5. `src/xai/base.py` uses legacy `Union` syntax**  
*File:* `src/xai/base.py`, line 22  
*Clause:* `def explain_or_reject(self, X: np.ndarray) -> Union[ExplanationCard, RejectionCard]:`  
*Issue:* The file already has `from __future__ import annotations`, and the project targets Python 3.10+. `ExplanationCard | RejectionCard` is cleaner and consistent with modern Python.  
*Recommended change:* Replace `Union[ExplanationCard, RejectionCard]` with `ExplanationCard | RejectionCard` and remove the `Union` import.

**6. `GateStatus` type hint claims `float` but stores `int`**  
*File:* `src/xai/gates.py`, lines 40–42  
*Clause:* `current: Mapping[str, float]` and `required: Mapping[str, float]`  
*Issue:* `evaluate_convergence` stores `"divergences": int(divergences)` in `current`, and `required` maps `"divergences"` to `DIVERGENCES_MAX: int = 0`. The test `test_divergences_kept_as_int` explicitly asserts that the value is an `int`, contradicting the `float` annotation. Harmless at runtime, but mypy (advisory in CI) may complain.  
*Recommended change:* Change the annotation to `Mapping[str, Union[int, float]]` or, with `__future__` annotations, `Mapping[str, int | float]`.

**7. `verify.py` truncates failure detail at 4000 characters**  
*File:* `tools/verify.py`, line 190  
*Clause:* `detail = str(c["detail"])[:4000]`  
*Issue:* A verbose flake8 or pytest failure can exceed 4000 characters. The truncation is silent (no "…[truncated]" indicator), which may hide the root cause when a reviewer reads the saved report.  
*Recommended change:* Append `"\n...[truncated]"` when truncation occurs, or raise the limit.

---

## Answers to checks

### Check 1 — src/xai correctness

**Clean.**

- **Card validation semantics:** `ExplanationCard` enforces non-empty strings via `_require_non_empty` (whitespace-only rejected), confidence in the closed interval `[0.0, 1.0]`, and `DataQuality` enum-member validation via `isinstance` (`test_plain_string_data_quality_rejected`). `RejectionCard` enforces enum-member validation, non-empty `recommendation`/`data_source`, and rejects bare strings/bytes for `missing_requirements`.
- **Deep-freeze:** `_deep_freeze` recursively converts mappings to `MappingProxyType` and sequences to tuples. Tests confirm that mutating the caller's original dict or nested containers does not leak into the card (`test_technical_detail_is_deeply_immutable`, `test_nested_payload_is_recursively_frozen`).
- **EvidenceGate `>=` semantics:** `EvidenceGate.evaluate` uses `observed[key] < float(required)`, so exact threshold values meet the gate. Boundary test at `test_boundary_value_meets_gate` confirms.
- **Absent-key handling:** Absent keys default to `0.0` via `current.get(key, 0.0)`. `test_absent_evidence_counts_as_zero` confirms.
- **`evaluate_convergence` strict boundaries:** Pass requires `r_hat < 1.01`, `ess_bulk > 400`, `ess_tail > 400`, `divergences == 0`. Boundary values (1.01, 400, 400, 0) are confirmed to fail in `test_boundary_values_fail_strictly`.
- **ABC contract:** `ExplainableModel` is `abc.ABC` with a single `@abc.abstractmethod` `explain_or_reject`. Subclassing without overriding raises `TypeError` at instantiation, which is the correct Python contract enforcement.

### Check 2 — Test quality

**Mostly clean; one Major finding (global coverage gate).**

- **Unit/integration tests:** The XAI unit tests (`test_xai_cards.py`, `test_xai_gates.py`) pin behaviour rather than mirroring implementation — they test contract invariants (immutability, validation, deep-freeze) that any correct implementation must satisfy. The integration smoke test (`test_xai_smoke.py`) exercises the full pipeline (gate → rejection or explanation → determinism) with a toy model.
- **Stub-contract engine soundness:**
  - *Silent mis-discovery:* Prevented by `test_discovery_matches_pinned_surface_exactly`, which asserts that the discovered set equals `EXPECTED_SURFACE` exactly. Any rename, miss, or unexpected addition fails loudly.
  - *Silent pass:* Prevented because `test_stub_raises_not_implemented` asserts `pytest.raises(NotImplementedError)`. If a stub is accidentally implemented but not moved to `IMPLEMENTED`, the test fails because the real code no longer raises.
  - *Break on graduation:* No. The implementer adds the qualified name to `IMPLEMENTED`, the contract test skips via `pytest.skip`, and real tests in a separate file take over. The notebook gate (`check_notebooks.py`) then demands the companion notebook.
- **Coverage gate honesty:** Asserting `NotImplementedError` for every stub line is a legitimate mechanism to establish a pre-implementation coverage baseline. When a stub graduates, its `raise` line is replaced by real code; if real tests are inadequate, the global average drops. The mechanism is sound, but see **Major finding 1** — the global gate is not a per-module guarantee.

### Check 3 — Gate tools

**Mostly clean; two Minor findings.**

- **`check_data_cards.py` edge cases:** The restricted-frontmatter parser correctly handles colons in URLs (splits on first `:` only), strips inline comments only when preceded by whitespace (preserving bare URL fragments), and rejects empty list items. See **Minor finding 2** for the spaced-hash footgun.
- **`check_notebooks.py` AST design:** The coupling to `test_stub_contracts.py` is deliberate and documented, but brittle. See **Minor finding 3**.
- **`verify.py` binary verdict:** Correct. A hard gate with status `FAIL` or `UNAVAILABLE` forces `verdict == "FAIL"`. Advisory gates (mypy) do not block. The deferred coverage gate (status `DEFERRED`) does not block. Exit code is `0` on PASS, `1` on FAIL.
- **`ci.yml` single source of truth:** Correct. The workflow calls `python tools/verify.py` and nothing else for quality gates. It uploads artifacts with `if: always()`, ensuring reports are available even on failure.

### Check 4 — Governance coherence

**Clean.**

The 10 invariants in `docs/INVARIANTS.md` are enforceable exactly as claimed:

- **Automated gate:** LINV-005 (data-card schema via `check_data_cards.py`), LINV-010 (notebook existence via `check_notebooks.py` for graduated modules), LINV-003 (convergence constants unit-tested in `gates.py`).
- **Tests:** LINV-001/002/008 (XAI contract, determinism).
- **Review:** LINV-004/006/007 (missing-data indicators, wide-prior justification, config provenance) are explicitly labeled as review-enforced or aspiration until Phase 2 modules graduate.

No invariant is dressed as full CI automation when it is not. The enforcement legend is honest.

### Check 5 — Curriculum

**Clean.**

- **`research_log.md`:** The milestone plan is coherent with the "derive in NumPy → rebuild in PyMC → compare" charter. Phase 2 breaks the Bayesian milestones into three model families (hierarchical, state-space/Kalman, survival) with explicit evidence gates and convergence thresholds, matching `src/xai/gates.py`. Week counts (14–26 for Phase 2) are realistic for hand-derivation plus PyMC rebuild. The 44-week Feb–Dec window provides buffer.
- **`learning-resources.md`:** Resources are keyed to phases and milestones. Phase 2 resources are hierarchically organized (warm-up → M2a → M2b → M2c). The capstone references (KALRO, KMD, Molnar) align with Phase 4 content.

### Check 6 — Config/data

**Clean.**

- **`kilifi_crops.yaml`:** Structurally valid. Every crop entry carries `basis: "literature"` and a `kalro_reference`. Units are declared in the top-level `provenance.units` block. Season definitions (`masika` MAM, `vuli` OND) match the KMD calendar referenced in `learning-resources.md`.
- **Data cards vs checker schema:** Both `DC-usda-nass-quickstats.md` and `DC-kalro-kilifi-crops.md` pass the required scalar and list fields. `status: draft` is within `ALLOWED_STATUS`.
- **Inconsistencies:** None found. The USDA card's "see future card" note for NASA POWER is a planned gap, not a contradiction. The KALRO card's crop list matches the YAML exactly (9 crops). Provenance fields in the YAML (`kalro_reference`, `basis`) are consistent with the card description.

### Check 7 — Cross-cutting

**Mostly clean.**

- **Contradictions:** None found between README, INVARIANTS, `research_log`, and tools.
- **First-stub graduation:** The mechanics are coherent. When the first stub graduates, the implementer must: (1) write real code, (2) write real unit tests in `tests/unit/`, (3) add the qualified name to `IMPLEMENTED`, (4) create the companion notebook. Missing (2) risks coverage drop; missing (3) causes the contract test to fail; missing (4) causes `check_notebooks.py` to fail. The system correctly breaks if any step is missed. See **Major finding 1** about the global coverage blind spot.
