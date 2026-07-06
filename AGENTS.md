# AGENTS.md — bayesrisk

Guidance for AI agents (Codex, Claude, etc.) working in this repository. bayesrisk uses a
multi-backend independent-review setup: the `scripts/*_review.sh` wrappers dispatch one
review prompt to several independent models and reconcile the results.

## The one rule
**Use the `scripts/*_review.sh` wrappers. NEVER call the raw CLIs (`gemini`, `claude`,
`codex`, `aichat`) directly.** The wrappers resolve keys/auth, set the node PATH, sandbox
read-only, timeout-guard, and stamp provenance. Do **not** set API keys yourself, and do
**not** export `ANTHROPIC_API_KEY` (it hijacks Claude's subscription).

## The wrappers
Run from the repo root; each writes `reviews/<tool>/<slug>.md` with a provenance header.
Prompt goes on stdin (heredoc) or via `-p FILE`. List every input file as args (used for
existence-check + provenance; the agentic backends also read them from the repo).

| Wrapper | Backend / default model | How it reads | Execute? | Timeout |
|---|---|---|---|---|
| `deepseek_review.sh` | DeepSeek — aichat **inline** (default), or `-A` **agentic** via Claude harness @ `api.deepseek.com/anthropic` (`deepseek-v4-pro`) | inlines `<files>` / agentic explores repo | `-A --exec` | 400 / 900s |
| `gemini_review.sh` | Gemini via **Vertex AI** (`gemini-2.5-pro`) | reads repo itself | **`--exec`** runs commands | 500 / 1800s |
| `claude_review.sh` | Claude (`sonnet`; subscription→API) | reads repo itself | read-only | 500s |
| `codex_review.sh` | Codex (GPT-5.x; subscription→API) | reads repo itself | read-only | **900s** (slowest) |
| `kimi_review.sh` | Kimi (`kimi-k2.6`) via Claude harness @ `api.moonshot.ai/anthropic` | reads repo itself | read-only | 500s |
| `glm_review.sh` | GLM (`glm-5.2`) via Claude harness @ `api.z.ai/api/anthropic` | reads repo itself | read-only | 500s |
| `reconcile_reviews.sh` | merges the above (synthesis via DeepSeek) | inlined | — | 200s |

Uniform invocation:
```bash
timeout -k 5 -s KILL <secs> scripts/<tool>_review.sh -o reviews/<tool>/<slug>.md -p /tmp/p.txt <files...>
```
- Override model with `-m <model>`.
- **Execute-heavy audits** (run scripts / reproduce metrics): `gemini_review.sh --exec` and
  `deepseek_review.sh -A --exec`. Default is read-only.
- Interactive agentic cockpits also exist: `deepseek-shell`, `kimi-shell`, `glm-shell`
  (Claude Code harness + that model's brain; add `--dangerously-skip-permissions` to execute).

## Designing a review prompt
Self-contained — the models have no repo context beyond what you attach/name:
- **Role** + **Task** (what to review, against what).
- **`Read:` list** naming EVERY file. DeepSeek-inline gets the contents; the agentic
  backends read them from the repo — either way, name them.
- **Enumerated, verifiable checks.**
- **House output format:** verdict first, then findings by severity (Blocker / Major /
  Minor / Observation), each with `file §clause`, the issue, why it matters, and a fix.
- **Rules:** "use only the attached files; cite exact file+clause; if a check is clean, say so."

## Auth (automatic — do not touch)
- DeepSeek `DEEPSEEK_API_KEY`, Kimi `MOONSHOT_API_KEY`, GLM `ZAI_API_KEY` — all in `~/.bashrc`.
- **Gemini = Vertex AI via ADC** (`GOOGLE_GENAI_USE_VERTEXAI=true` + `GOOGLE_CLOUD_PROJECT`/
  `GOOGLE_CLOUD_LOCATION` in `~/.bashrc`; `~/.gemini/settings.json` auth `vertex-ai`; creds
  at `~/.config/gcloud/application_default_credentials.json`). No API key. Avoids the
  free-tier AI-Studio rate wall.
- Claude / Codex: subscription first, API-key fallback (provenance stamps which).

## Reconcile & report
```bash
scripts/reconcile_reviews.sh -o reviews/reconciled/<slug>.md reviews/*/<slug>.md
```
Lead with the consensus verdict; surface where reviewers diverge. A single backend's
"no findings" is **not** sign-off — any one reviewer's finding is worth a human look.

## Failure handling
On failure a wrapper prints `FAILED (<tool>): …` or `<tool>_review.sh: aborted at line N` —
**report that; do not retry the raw CLI.** Notes:
- **Gemini** needs `--exec` (and Vertex credits) to actually run commands; without it it can
  only read/reason and will say checks were "not run".
- **Kimi**'s harness path can hang if Moonshot's Anthropic endpoint is degraded — that's not
  a quota; skip Kimi and use the others if so.
- The gemini CLI returns an empty report on one huge exhaustive prompt — for big audits,
  chunk into bounded per-dimension prompts and assemble.
