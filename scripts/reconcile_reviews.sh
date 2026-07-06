#!/usr/bin/env bash
#
# scripts/reconcile_reviews.sh
# Merge several independent review reports of the SAME package into one consensus
# report. Runs via deepseek_review.sh (the reports are inlined; a fixed synthesis
# prompt drives the merge). See AGENTS.md §5.2 (Synthesis / Reconciliation).
#
# Usage:
#   scripts/reconcile_reviews.sh -o reviews/reconciled/<slug>.md [-m model] <report>...
#   e.g. reconcile_reviews.sh -o reviews/reconciled/v1-028_reconciled.md \
#          reviews/deepseek/v1-028_*.md reviews/gemini/v1-028_*.md \
#          reviews/claude/v1-028_*.md reviews/codex/v1-028_*.md
#
# Options:
#   -o FILE   output report path (required)
#   -m MODEL  DeepSeek model (default deepseek-v4-flash)
set -eo pipefail

MODEL="deepseek-v4-flash"; OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    -o) OUT="$2"; shift 2;;
    -m) MODEL="$2"; shift 2;;
    --) shift; break;;
    -*) echo "unknown option: $1" >&2; exit 2;;
    *) break;;
  esac
done
[ -n "$OUT" ] || { echo "usage: $0 -o <out.md> [-m model] <report>... (>=2 reports)" >&2; exit 2; }
[ "$#" -ge 2 ] || { echo "error: give at least two report files to reconcile" >&2; exit 2; }
for f in "$@"; do [ -f "$f" ] || { echo "missing report: $f" >&2; exit 2; }; done

# locate deepseek_review.sh (on PATH, or alongside this script)
DR="$(command -v deepseek_review.sh 2>/dev/null || true)"
[ -n "$DR" ] || DR="$(dirname "$0")/deepseek_review.sh"
[ -x "$DR" ] || { echo "deepseek_review.sh not found (needed to run the merge)" >&2; exit 3; }

prompt="$(mktemp)"; trap 'rm -f "$prompt"' EXIT
cat > "$prompt" <<'EOF'
You are given several independent review reports of the SAME package, each produced by a
different reviewer (the reviewer/tool is identifiable from each report's provenance header
and filename). Using ONLY the attached reports, produce ONE reconciled report.

Rules:
- Deduplicate findings across reviewers: list each distinct issue once, noting which
  reviewer(s) raised it and the severity each assigned.
- State the consensus where reviewers agree. Where they DISAGREE (e.g., one reports a
  Blocker/Major and another rates the package clean), flag the divergence explicitly and
  present both positions with their exact file/clause citations.
- Preserve every finding's exact file and clause references.
- Do NOT introduce any finding that no attached report contains.
- Order findings by the highest severity any reviewer assigned (Blocker > Major > Minor).

End with, in this order:
1. A per-reviewer verdict table (reviewer -> verdict/severity summary).
2. Consensus verdict: accept / approve-after-fixes / not-acceptable-as-drafted / clean.
3. "Action before sign-off" list: every Blocker or Major raised by at least one reviewer.
4. A one-line reminder that a single reviewer's clearance is not sign-off.
EOF

"$DR" -o "$OUT" -m "$MODEL" -p "$prompt" "$@"
