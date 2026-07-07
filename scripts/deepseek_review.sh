#!/usr/bin/env bash
#
# scripts/deepseek_review.sh
# Run a DeepSeek review/audit and file a clean, provenance-stamped report.
#
# TWO modes:
#   • INLINE (default) — aichat attaches the given files with -f (documents-only, read-only,
#     cheap, fast). Used by the align external-review protocol. See AGENTS.md.
#   • AGENTIC (-A/--agentic) — DeepSeek drives the Claude Code harness against DeepSeek's
#     Anthropic-compatible endpoint (https://api.deepseek.com/anthropic), so it reads/greps
#     the repo ITSELF like Claude/Codex. This path (not aichat's function-calling) is used
#     because it round-trips `reasoning_content`, avoiding DeepSeek's known multi-turn
#     tool-call bugs. Read-only by default; add --exec to let it RUN commands (for audits
#     that reproduce metrics). Input files optional; it explores the repo root.
#
# Usage:
#   scripts/deepseek_review.sh -o reviews/deepseek/<slug>.md [opts] <input-file>...  <<'PROMPT'
#   ...prompt text...
#   PROMPT
#
# Options:
#   -o FILE       output report path (required)
#   -m MODEL      inline: deepseek-v4-flash (default) | deepseek-v4-pro
#                 agentic: deepseek-v4-pro[1m] (default) | deepseek-v4-flash  (brackets=1M ctx)
#   -r ROLE       inline only: aichat role (default auditor — temp 0)
#   -p FILE       read the prompt from FILE instead of stdin
#   --both        inline only: run flash AND pro; writes <slug>_v4flash.md and <slug>_v4pro.md
#   -A/--agentic  agentic mode via the Claude Code harness (DeepSeek reads files itself)
#   --exec        agentic only: allow command execution (--dangerously-skip-permissions);
#                 default agentic mode is read-only (--permission-mode plan)
#
# Exit codes: 2 usage/input error, 3 environment error, 1 API failure.
set -eo pipefail
trap 'rc=$?; echo "deepseek_review.sh: aborted at line $LINENO (exit $rc)" >&2' ERR

MODEL=""; ROLE="auditor"; OUT=""; PROMPT_FILE=""; BOTH=0; AGENTIC=0; EXEC=0
while [ $# -gt 0 ]; do
  case "$1" in
    -o) OUT="$2"; shift 2;;
    -m) MODEL="$2"; shift 2;;
    -r) ROLE="$2"; shift 2;;
    -p) PROMPT_FILE="$2"; shift 2;;
    --both) BOTH=1; shift;;
    -A|--agentic) AGENTIC=1; shift;;
    --exec) EXEC=1; shift;;
    --) shift; break;;
    -*) echo "unknown option: $1" >&2; exit 2;;
    *) break;;
  esac
done
[ -n "$OUT" ] || { echo "usage: $0 -o <out.md> [opts] <input-file>...  (prompt on stdin or -p FILE)" >&2; exit 2; }
if [ "$AGENTIC" = 0 ] && [ $# -eq 0 ]; then
  echo "error: no input files given (inline mode). Use -A/--agentic to let DeepSeek explore the repo itself." >&2; exit 2
fi

# aichat + key must be available even in non-interactive shells (bashrc may early-return)
export PATH="$HOME/.local/bin:$PATH"
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-$(grep -oP 'DEEPSEEK_API_KEY="\K[^"]+' "$HOME/.bashrc" 2>/dev/null | tail -1)}"
[ -n "${DEEPSEEK_API_KEY:-}" ] || { echo "DEEPSEEK_API_KEY not set and not found in ~/.bashrc" >&2; exit 3; }

# read prompt
if [ -n "$PROMPT_FILE" ]; then PROMPT="$(cat "$PROMPT_FILE")"; else PROMPT="$(cat)"; fi
[ -n "$PROMPT" ] || { echo "error: empty prompt (nothing on stdin / -p file)" >&2; exit 2; }

# ---------------------------------------------------------------- AGENTIC (Claude harness)
if [ "$AGENTIC" = 1 ]; then
  # The claude CLI is a node app; ensure nvm node is on PATH.
  NODE_BIN="$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1 || true)"
  [ -n "$NODE_BIN" ] && export PATH="$NODE_BIN:$PATH"
  command -v claude >/dev/null || { echo "claude CLI not found (it's the agentic harness for DeepSeek)" >&2; exit 3; }
  command -v node   >/dev/null || { echo "node not found on PATH (nvm not loaded)" >&2; exit 3; }
  [ -n "$MODEL" ] || MODEL="deepseek-v4-pro[1m]"        # agentic default: strongest, 1M ctx
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

  # Point Claude Code at DeepSeek's Anthropic-compatible endpoint; force DeepSeek on every
  # tier; drop any real Anthropic key so it can't hijack the endpoint.
  export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
  export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
  export ANTHROPIC_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
  export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
  export CLAUDE_CODE_EFFORT_LEVEL="${CLAUDE_CODE_EFFORT_LEVEL:-max}"
  unset ANTHROPIC_API_KEY

  perm=(--permission-mode plan); mode="read-only"
  if [ "$EXEC" = 1 ]; then perm=(--dangerously-skip-permissions); mode="EXECUTE"; fi

  raw="$(mktemp)"; err="$(mktemp)"; trap 'rm -f "$raw" "$err"' EXIT
  echo ">>> deepseek:$MODEL (AGENTIC via Claude harness @ api.deepseek.com/anthropic, $mode) -> $OUT" >&2
  # cd into $ROOT and DROP --add-dir (pre-indexing the whole tree each turn is slow on the
  # Anthropic-compatible endpoint and can time out on big repos); cwd=$ROOT reads the repo fast.
  if ! ( cd "$ROOT" && printf '%s' "$PROMPT" | claude -p --output-format text "${perm[@]}" >"$raw" 2>"$err" ); then
    echo "FAILED (deepseek via claude harness):" >&2; sed 's/^/    /' "$err" >&2; exit 1
  fi
  clean="$(sed '/./,$!d' "$raw")"; [ -n "$clean" ] || clean="$(cat "$raw")"
  if [ -z "$(printf '%s' "$clean" | tr -d '[:space:]')" ]; then
    echo "FAILED (deepseek): empty body — raw stdout head + stderr tail:" >&2
    head -30 "$raw" | sed 's/^/    /' >&2; tail -15 "$err" | sed 's/^/    /' >&2; exit 1
  fi
  mkdir -p "$(dirname "$OUT")"
  {
    printf '# %s\n\n' "$(basename "${OUT%.md}")"
    printf '> Generated by DeepSeek (`%s`) via api.deepseek.com/anthropic + Claude Code harness (%s) on %s.\n' \
      "$MODEL" "$mode" "$(date '+%F %T %Z')"
    printf '> Working dir: %s\n\n---\n\n' "$ROOT"
    printf '%s\n' "$clean"
  } > "$OUT"
  echo "    wrote $OUT ($(wc -l <"$OUT") lines)" >&2
  exit 0
fi

# ---------------------------------------------------------------- INLINE (aichat -f)
command -v aichat >/dev/null || { echo "aichat not found on PATH (~/.local/bin)" >&2; exit 3; }
[ -n "$MODEL" ] || MODEL="deepseek-v4-flash"

INPUTS=("$@"); FARGS=()
for f in "${INPUTS[@]}"; do [ -f "$f" ] || { echo "missing input file: $f" >&2; exit 2; }; FARGS+=(-f "$f"); done

strip_think() { if command -v perl >/dev/null 2>&1; then perl -0777 -pe 's{<think>.*?</think>\s*}{}gs'; else cat; fi; }

run_one() {
  local model="$1" out="$2" raw
  raw="$(mktemp)"
  echo ">>> deepseek:$model (role $ROLE, ${#INPUTS[@]} inlined) -> $out" >&2
  # </dev/null: prompt is an argument; aichat must not block on inherited stdin.
  if ! aichat -S -r "$ROLE" -m "deepseek:$model" "${FARGS[@]}" "$PROMPT" </dev/null >"$raw" 2>&1; then
    echo "FAILED (deepseek:$model):" >&2; sed 's/^/    /' "$raw" >&2; rm -f "$raw"; return 1
  fi
  mkdir -p "$(dirname "$out")"
  {
    printf '# %s\n\n' "$(basename "${out%.md}")"
    printf '> Generated by aichat + DeepSeek (`deepseek:%s`, role `%s`) on %s.\n' \
      "$model" "$ROLE" "$(date '+%F %T %Z')"
    printf '> Inputs (%d): %s\n\n---\n\n' "${#INPUTS[@]}" "${INPUTS[*]}"
    strip_think < "$raw"
  } > "$out"
  echo "    wrote $out ($(wc -l <"$out") lines)" >&2
  rm -f "$raw"
}

if [ "$BOTH" = 1 ]; then
  base="${OUT%.md}"
  run_one deepseek-v4-flash "${base}_v4flash.md"
  run_one deepseek-v4-pro   "${base}_v4pro.md"
else
  run_one "$MODEL" "$OUT"
fi
