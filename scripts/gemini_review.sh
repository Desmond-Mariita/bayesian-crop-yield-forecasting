#!/usr/bin/env bash
#
# scripts/gemini_review.sh
# Run a Gemini headless review/audit prompt and file a provenance-stamped report.
#
# Usage:
#   scripts/gemini_review.sh -o reviews/gemini/<slug>.md [opts] <input-file>... <<'PROMPT'
#   ...prompt text...
#   PROMPT
#
# Options:
#   -o FILE     output report path (required; convention: reviews/gemini/<slug>.md)
#   -m MODEL    Gemini model name; omit to use the CLI default
#   -p FILE     read the prompt from FILE instead of stdin
#   --exec      allow command execution (--yolo, auto-approves all tool calls) — needed for
#               audits that RUN scripts. Default is read-only (--approval-mode plan), in
#               which Gemini can read files but NOT run commands (it will honestly report
#               "x was not run"). In exec mode the wrapper also KEEPS tool-call narration in
#               the report so you can verify Gemini actually ran things (see gemini-cli
#               #16423 "self-assured loop": it sometimes claims actions without executing).
#
# The CLI is run non-interactively with the repo root exposed via --include-directories so
# it can inspect/act on the named input files headlessly.

set -eo pipefail

# Never fail silently: if `set -e` aborts on some command, report where.
trap 'rc=$?; echo "gemini_review.sh: aborted at line $LINENO (exit $rc)" >&2' ERR

# The gemini CLI is a `#!/usr/bin/env node` script. Non-interactive shells skip
# ~/.bashrc's nvm load, so ensure the newest nvm node is on PATH.
NODE_BIN="$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$NODE_BIN" ]; then export PATH="$NODE_BIN:$PATH"; fi

MODEL=""; OUT=""; PROMPT_FILE=""; EXEC=0
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

command -v gemini >/dev/null || { echo "gemini not found on PATH" >&2; exit 3; }
command -v node   >/dev/null || { echo "node not found on PATH (nvm not loaded)" >&2; exit 3; }
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Auth: two modes.
#  (A) Vertex AI (preferred for agentic — no free-tier rate wall): triggered by
#      GOOGLE_GENAI_USE_VERTEXAI=true (env or ~/.bashrc). Uses ADC (gcloud
#      application-default login) + project/location; NO API key. Requires
#      ~/.gemini/settings.json auth selectedType = "vertex-ai".
#  (B) AI Studio API key: GEMINI_API_KEY/GOOGLE_API_KEY (env or grep ~/.bashrc).
# Non-interactive shells don't source ~/.bashrc, hence the greps.
VERTEX="${GOOGLE_GENAI_USE_VERTEXAI:-$(grep -oP 'GOOGLE_GENAI_USE_VERTEXAI=\K\S+' "$HOME/.bashrc" 2>/dev/null | tr -d '"' | tail -1 || true)}"
if [ "$VERTEX" = "true" ]; then
  export GOOGLE_GENAI_USE_VERTEXAI=true
  export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-$(grep -oP 'GOOGLE_CLOUD_PROJECT="\K[^"]+' "$HOME/.bashrc" 2>/dev/null | tail -1 || true)}"
  export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-$(grep -oP 'GOOGLE_CLOUD_LOCATION="\K[^"]+' "$HOME/.bashrc" 2>/dev/null | tail -1 || true)}"
  # gcloud on PATH so the google-auth lib can refresh the ADC token headlessly
  [ -d "$HOME/google-cloud-sdk/bin" ] && export PATH="$HOME/google-cloud-sdk/bin:$PATH"
  unset GEMINI_API_KEY GOOGLE_API_KEY
  authdesc="Vertex AI (${GOOGLE_CLOUD_PROJECT}/${GOOGLE_CLOUD_LOCATION})"
  # Default to gemini-2.5-pro: accessible on this Vertex project AND stable across gemini-cli
  # versions (0.49+ silently remaps the bare 'gemini-2.5-flash' alias to gemini-3.5-flash,
  # which the project can't access → 404). 'gemini-2.5-flash-lite' is a cheaper stable option.
  [ -n "$MODEL" ] || MODEL="gemini-2.5-pro"
else
  if [ -z "${GEMINI_API_KEY:-}" ] && [ -n "${GOOGLE_API_KEY:-}" ]; then export GEMINI_API_KEY="$GOOGLE_API_KEY"; fi
  if [ -z "${GEMINI_API_KEY:-}" ]; then
    _gk="$(grep -oP '(GEMINI|GOOGLE)_API_KEY="\K[^"]+' "$HOME/.bashrc" 2>/dev/null | tail -1 || true)"
    if [ -n "$_gk" ]; then export GEMINI_API_KEY="$_gk"; fi
  fi
  authdesc="AI Studio API key"
fi

if [ -n "$PROMPT_FILE" ]; then PROMPT="$(cat "$PROMPT_FILE")"; else PROMPT="$(cat)"; fi
[ -n "$PROMPT" ] || { echo "error: empty prompt (nothing on stdin / -p file)" >&2; exit 2; }

INPUTS=("$@")
for f in "${INPUTS[@]}"; do [ -f "$f" ] || { echo "missing input file: $f" >&2; exit 2; }; done

raw="$(mktemp)"; err="$(mktemp)"
trap 'rm -f "$raw" "$err"' EXIT

# exec: --yolo auto-approves ALL tool calls so Gemini actually RUNS commands headlessly
# (in default/plan mode a shell tool call waits for approval that never comes → skipped).
# read-only: --approval-mode plan (reads files, cannot run commands).
if [ "$EXEC" = 1 ]; then
  # --skip-trust alone is NOT enough: an untrusted workspace silently overrides --yolo back
  # to "default" (→ tool calls block/hang headlessly). GEMINI_CLI_TRUST_WORKSPACE=true makes
  # --yolo actually stick. NOTE: heavy agentic runs on a FREE-tier AIza key hit
  # RATE_LIMIT_EXCEEDED and back off 60-70s per call (looks like a hang) — use a paid/Vertex
  # key or a flash model (-m) for real agentic audits; give a long timeout to survive backoffs.
  export GEMINI_CLI_TRUST_WORKSPACE=true
  gemini_args=(--output-format text --yolo --skip-trust --include-directories "$ROOT"); mode="EXECUTE (--yolo)"
else
  gemini_args=(--output-format text --approval-mode plan --skip-trust --include-directories "$ROOT"); mode="read-only (plan)"
fi
[ -n "$MODEL" ] && gemini_args+=(--model "$MODEL")
echo ">>> gemini ($mode) -> $OUT" >&2

# Gemini intermittently returns narration-only / EMPTY stdout with exit 0 — the "self-assured
# loop" (gemini-cli #16423) — and the wrapper used to write a header-only (silently empty)
# report while discarding the deleted-on-exit temp files. So: RETRY on an empty body, and if it
# stays empty, FAIL LOUDLY with the raw evidence so callers / reconcile / retry logic catch it.
# Tune attempts with GEMINI_MAX_TRIES (default 3).
MAX_TRIES="${GEMINI_MAX_TRIES:-3}"; clean=""; attempt=0
while [ "$attempt" -lt "$MAX_TRIES" ]; do
  attempt=$((attempt+1))
  if ! gemini "${gemini_args[@]}" --prompt "$PROMPT" </dev/null >"$raw" 2>"$err"; then
    echo "FAILED (gemini) attempt $attempt/$MAX_TRIES:" >&2; sed 's/^/    /' "$err" >&2
    [ "$attempt" -lt "$MAX_TRIES" ] && { echo "    retrying…" >&2; sleep 2; continue; }
    exit 1
  fi
  # Clean CLI/system noise. READ-ONLY also strips "I will…/Let me…" narration and starts at the
  # first heading; EXEC keeps narration (it is the evidence of what Gemini actually ran).
  if [ "$EXEC" = 1 ]; then
    clean="$(grep -vE "^(Warning:|Approval mode |Ripgrep|Loaded cached|Data collection|\(node:[0-9]+\)|\(Use \`node)" "$raw" | sed '/./,$!d' || true)"
    [ -n "$clean" ] || clean="$(cat "$raw")"
  else
    body="$(grep -vE "^(Warning:|Approval mode |Ripgrep|Loaded cached|Data collection|\(node:[0-9]+\)|\(Use \`node|Error executing tool |I will |I'll |Let me |First, I |Next, I |Now I |I am going to |I need to )" "$raw" || true)"
    clean="$(printf '%s\n' "$body" | awk 'f||/^#/{f=1} f')"
    [ -n "$clean" ] || clean="$(printf '%s\n' "$body" | sed '/./,$!d')"
  fi
  [ -n "$(printf '%s' "$clean" | tr -d '[:space:]')" ] && break
  echo "gemini: EMPTY body (attempt $attempt/$MAX_TRIES) — narration-only/empty-final (#16423); retrying…" >&2
  clean=""; sleep 2
done
if [ -z "$(printf '%s' "$clean" | tr -d '[:space:]')" ]; then
  echo "FAILED (gemini): empty body after $MAX_TRIES attempts (self-assured-loop / empty-final, gemini-cli #16423)." >&2
  echo "    --- last raw stdout (head) ---" >&2; head -40 "$raw" | sed 's/^/    /' >&2
  echo "    --- last stderr (tail) ---"     >&2; tail -20 "$err" | sed 's/^/    /' >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
{
  printf '# %s\n\n' "$(basename "${OUT%.md}")"
  printf '> Generated by Gemini CLI (model `%s`, %s, auth: %s) on %s.\n' \
    "${MODEL:-default}" "$mode" "$authdesc" "$(date '+%F %T %Z')"
  printf '> Inputs (%d): %s\n\n---\n\n' "${#INPUTS[@]}" "${INPUTS[*]}"
  printf '%s\n' "$clean"
} > "$OUT"
