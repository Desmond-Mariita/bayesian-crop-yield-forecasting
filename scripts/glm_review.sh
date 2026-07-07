#!/usr/bin/env bash
#
# scripts/glm_review.sh
# Run an AGENTIC review with GLM (Zhipu / Z.ai) by driving the Claude Code harness against
# Z.ai's Anthropic-compatible endpoint. GLM reads/greps the repo itself (like Claude/Codex),
# then files a provenance-stamped report. Needs ZAI_API_KEY (env or ~/.bashrc).
#
# Usage:
#   scripts/glm_review.sh -o reviews/glm/<slug>.md [opts] <input-file>... <<'PROMPT'
#   ...prompt text...
#   PROMPT
#
# Options:
#   -o FILE   output report path (required; convention: reviews/glm/<slug>.md)
#   -m MODEL  GLM model (default 'glm-4.7' — budget-friendly (use glm-5.2[1m] for 1M context); or set GLM_MODEL)
#   -p FILE   read the prompt from FILE instead of stdin
#   --exec    auto-approve tool calls (--dangerously-skip-permissions) so GLM can EXECUTE —
#             write files / run commands. Needed when the prompt tells GLM to persist the
#             review to disk itself (or run scripts): in the default read-only plan mode such
#             a prompt stalls at the "plan approved?" gate headlessly and exits without doing
#             the review. Default stays read-only (plan): the review is captured from stdout.

set -eo pipefail
trap 'rc=$?; echo "glm_review.sh: aborted at line $LINENO (exit $rc)" >&2' ERR

# The claude CLI is a `#!/usr/bin/env node` script; ensure nvm node is on PATH.
NODE_BIN="$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$NODE_BIN" ]; then export PATH="$NODE_BIN:$PATH"; fi

MODEL="${GLM_MODEL:-glm-4.7}"; OUT=""; PROMPT_FILE=""; EXEC=0
while [ $# -gt 0 ]; do
  case "$1" in
    -o) OUT="$2"; shift 2;;
    -m) MODEL="$2"; shift 2;;
    -p) PROMPT_FILE="$2"; shift 2;;
    --exec) EXEC=1; shift;;
    --) shift; break;;
    -*) echo "unknown option: $1" >&2; exit 2;;
    *) break;;
  esac
done
[ -n "$OUT" ] || { echo "usage: $0 -o <out.md> [opts] <input-file>...  (prompt on stdin or -p FILE)" >&2; exit 2; }
[ $# -gt 0 ] || { echo "error: no input files given" >&2; exit 2; }

command -v claude >/dev/null || { echo "claude CLI not found on PATH (it's the harness for GLM here)" >&2; exit 3; }
command -v node   >/dev/null || { echo "node not found on PATH (nvm not loaded)" >&2; exit 3; }
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [ -n "$PROMPT_FILE" ]; then PROMPT="$(cat "$PROMPT_FILE")"; else PROMPT="$(cat)"; fi
[ -n "$PROMPT" ] || { echo "error: empty prompt (nothing on stdin / -p file)" >&2; exit 2; }

INPUTS=("$@")
for f in "${INPUTS[@]}"; do [ -f "$f" ] || { echo "missing input file: $f" >&2; exit 2; }; done

# Resolve the Z.ai key (env or ~/.bashrc; works in non-interactive shells).
KEY="${ZAI_API_KEY:-$(grep -oP 'ZAI_API_KEY="\K[^"]+' "$HOME/.bashrc" 2>/dev/null | tail -1 || true)}"
[ -n "$KEY" ] || { echo "ZAI_API_KEY not set and not found in ~/.bashrc" >&2; exit 3; }

# Point the Claude Code harness at Z.ai's Anthropic-compatible endpoint, forcing the GLM
# model on every tier. Unset any real Anthropic key so it can't override the endpoint.
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="$KEY"
export ANTHROPIC_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
export CLAUDE_CODE_SUBAGENT_MODEL="$MODEL"
unset ANTHROPIC_API_KEY

raw="$(mktemp)"; err="$(mktemp)"
trap 'rm -f "$raw" "$err"' EXIT

# -p headless, text output, plan (read-only). Run FROM the repo root (cd) and DO NOT pass
# --add-dir: --add-dir makes claude pre-index the whole tree each turn (much slower per call on
# Anthropic-compatible endpoints), so multi-file reviews can blow past the timeout. cwd=$ROOT
# lets claude read the repo directly; the subshell keeps the outer cwd (and -o path) intact.
# The prompt is piped in on stdin (printf), which reaches EOF so the CLI won't block.
# Permission mode: default plan (read-only; the review is captured from stdout). --exec switches
# to --dangerously-skip-permissions so GLM can WRITE/RUN — required when the prompt instructs GLM
# to persist the review itself or execute scripts (plan mode otherwise stalls at the "plan
# approved?" gate headlessly and exits without doing the review).
if [ "$EXEC" = 1 ]; then perm=(--dangerously-skip-permissions); mode="EXECUTE"; else perm=(--permission-mode plan); mode="read-only (plan)"; fi
echo ">>> glm:$MODEL ($mode) -> $OUT" >&2
if ! ( cd "$ROOT" && printf '%s' "$PROMPT" | claude -p --output-format text "${perm[@]}" >"$raw" 2>"$err" ); then
  echo "FAILED (glm via claude harness):" >&2
  sed 's/^/    /' "$err" >&2
  exit 1
fi

clean="$(sed '/./,$!d' "$raw")"
[ -n "$clean" ] || clean="$(cat "$raw")"
if [ -z "$(printf '%s' "$clean" | tr -d '[:space:]')" ]; then
  echo "FAILED (glm): empty body — raw stdout head + stderr tail:" >&2
  head -30 "$raw" | sed 's/^/    /' >&2; tail -15 "$err" | sed 's/^/    /' >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
{
  printf '# %s\n\n' "$(basename "${OUT%.md}")"
  printf '> Generated by GLM (`%s`) via Z.ai Anthropic-compatible endpoint + Claude Code harness on %s.\n' \
    "$MODEL" "$(date '+%F %T %Z')"
  printf '> Inputs (%d): %s\n\n---\n\n' "${#INPUTS[@]}" "${INPUTS[*]}"
  printf '%s\n' "$clean"
} > "$OUT"
