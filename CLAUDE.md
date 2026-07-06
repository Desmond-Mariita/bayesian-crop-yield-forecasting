# CLAUDE.md — bayesrisk

Guidance for Claude agents working in this repository. Review mechanics, the wrapper table,
prompt design, model/auth details, and the `--exec` / `-A` flags live in `AGENTS.md` — read it.

## Review policy (Claude is the orchestrator)

Two kinds of review. **Both must be saved to disk — never keep a review only in the conversation.**

**Internal review** = Claude spins up **subagents (Sonnet)** to critique the work.
- Claude decides how many, but the count **must not exceed 5**.
- Run **at most 2 subagents at a time**.
- Among the (up to 5) there **must be a devil's-advocate / red-team** agent — whichever is
  applicable — whose job is to attack the work and find what's wrong, not to confirm it.

**External review** = calling the other LLMs via the `scripts/*_review.sh` wrappers
(procedure below + `AGENTS.md`).

**Deep-analysis rule:** any task that requires deep analysis **MUST include Codex's
review/feedback**. If the **Codex review fails for any reason** (auth, timeout, error, empty
output), **inform the User (Desmond) and STOP until advised** — do not silently proceed
without it.

**Persistence:** **ALL internal and external reviews MUST be saved to disk.** External →
`reviews/<tool>/<slug>.md`; internal subagent critiques → `reviews/internal/<slug>-<role>.md`
(e.g. `-redteam`, `-correctness`). Reconcile external panels → `reviews/reconciled/<slug>.md`.

**Standards gate:** `developer_guidelines.txt` **must be strictly adhered to and enforced by
CI.** A guidelines/CI failure is a blocker — do not merge or claim done over it. (Guidelines
cover: Google-style docstrings + type hints everywhere, `pathlib` only, `logging` not
`print`, no magic numbers, mandatory unit+integration tests, fixed/logged RNG seeds,
artifacts under `reports/` with timestamps, plan-before-code with checkpoints and 1–2 atomic
tasks per step, feature branches + rebase-then-merge.)

Enforcement is live from commit one via **two gates**: a git **pre-commit hook**
(`.githooks/pre-commit`) and **CI** (`.github/workflows/ci.yml`). Both run
`tools/check_guidelines.py` (docstrings, type hints, no `print`, imports); CI additionally
runs flake8, `black --check`, mypy (advisory), and **pytest with a ≥90% coverage gate**
(`--cov-fail-under=90`, the MedInsight standard — deferred until the first test exists, then
enforced). Do not `--no-verify` past these without Desmond's OK.

### Verification — rules of engagement
Modelled on MedInsight (ADR-048 / `POLICING_TOOLS.md`): **the agent runs verification and
produces the report; Desmond reviews the report, not the raw run.**
- Claude **runs `python tools/verify.py`** at every checkpoint that needs it — before
  claiming a task done, before any merge, and after any deep-analysis task. It executes all
  gates (guidelines, flake8, black, mypy-advisory, pytest + ≥90% coverage) and writes a
  **timestamped report** to `reports/verification/<ts>.md` (+ `.json`, + `latest.md`) with a
  **binary PASS/FAIL verdict**. That report is the artifact Desmond checks.
- **Halt-on-failure:** a FAIL verdict is a blocker — do not proceed, merge, or claim "done"
  on a FAIL. Fix and re-run until PASS (or, under the deep-analysis rule, stop and inform
  Desmond).
- **Every verification run is saved to disk** (like all reviews). Never report "verified"
  without the saved report backing it — evidence before claims.
- **Desmond's role** is to read `reports/verification/latest.md` (and the review reports),
  not to run the checks himself.

### Standing practice (from prior engagements)
- **Subagents run in Sonnet; the orchestrator stays on its own (Opus) model.** Keep each
  subagent's scope tight and independent so 2-at-a-time parallelism is safe and mergeable.
- **Use the wrappers, never the raw CLIs** (`AGENTS.md` "the one rule"). Auth is automatic —
  do not set API keys and do not export `ANTHROPIC_API_KEY`.
- **Evidence before claims:** run the check and quote the real output before declaring
  anything fixed/passing (mirrors the guidelines' "repro steps / confirm the fix").
- **Consensus, not majority-comfort:** lead with the reconciled verdict and surface where
  reviewers diverge — one backend's "no findings" is NOT sign-off.
- **Execute-heavy analysis:** Gemini needs `--exec` (runs via Vertex AI); DeepSeek `-A
  --exec`; chunk a large exhaustive audit into bounded per-dimension passes and assemble (the
  gemini CLI returns empty on one giant prompt); if Kimi's harness path hangs (Moonshot
  endpoint), skip it — it is not a quota limit.

## External review protocol

When the user asks for an **external review** (also: "outside review", "second opinion",
"independent review", "have the others review this"), do NOT rely on your own analysis
alone. You are Claude — the whole point is to get opinions from models *other than
yourself*. Obtain independent reviews from the external backends: **Gemini, Codex, and
DeepSeek** (add **Kimi** and **GLM** if the user wants a wider panel).

Procedure:

1. **Author one self-contained review prompt** (per `AGENTS.md` "Designing a review
   prompt"): role, task, an explicit `Read:` list naming every file, enumerated checks, the
   house findings/output format, and rules ("use only the attached files; cite exact
   file+clause; if a check is clean, say so"). Write it to `/tmp/review_prompt.txt`.

2. **Dispatch to the external backends**, each `timeout`-guarded, filing to
   `reviews/<tool>/<slug>.md`. Run them in parallel; Codex is slowest:

   ```bash
   cd <repo root>
   timeout -k 5 -s KILL 400 scripts/deepseek_review.sh -o reviews/deepseek/<slug>.md -p /tmp/review_prompt.txt <files> &
   timeout -k 5 -s KILL 500 scripts/gemini_review.sh   -o reviews/gemini/<slug>.md   -p /tmp/review_prompt.txt <files> &
   timeout -k 5 -s KILL 900 scripts/codex_review.sh    -o reviews/codex/<slug>.md    -p /tmp/review_prompt.txt <files> &
   wait
   ```
   DeepSeek **inlines** the file contents; Gemini and Codex are agentic and **read the files
   themselves** (so the prompt's `Read:` list must name every file). The `<files>` args are
   required for all three. For an **execute-heavy audit** (run scripts / reproduce results),
   add `--exec` to gemini and `-A --exec` to deepseek.

3. **Reconcile into one consensus report:**
   ```bash
   scripts/reconcile_reviews.sh -o reviews/reconciled/<slug>.md \
     reviews/deepseek/<slug>.md reviews/gemini/<slug>.md reviews/codex/<slug>.md
   ```

4. **Report the reconciled verdict:** lead with the consensus verdict and any Blocker/Major
   finding, and explicitly surface where the reviewers diverge. A single backend's "no
   findings" is NOT sign-off — a finding raised by any one reviewer is worth a human look.

Do not include a Claude review in the set (you are the agent). If the user explicitly asks
for the full panel, add `scripts/claude_review.sh`, `scripts/kimi_review.sh`, and
`scripts/glm_review.sh`.

Notes: Gemini runs via Vertex AI (needs `--exec` to execute); if Kimi's harness path hangs
(Moonshot endpoint), skip it and use the others; for a large exhaustive audit, chunk the
prompt into bounded per-dimension passes and assemble (the gemini CLI returns empty on one
giant prompt).
