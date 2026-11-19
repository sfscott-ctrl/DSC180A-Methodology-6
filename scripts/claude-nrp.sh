#!/usr/bin/env bash
# Keep the key in the process environment, never in project settings.
set -euo pipefail
if [[ -z "${ANTHROPIC_AUTH_TOKEN:-}" ]]; then
  read -r -s -p "NRP API token: " ANTHROPIC_AUTH_TOKEN
  printf '\n' >&2
fi
export ANTHROPIC_AUTH_TOKEN
export ANTHROPIC_API_KEY=""
export ANTHROPIC_BASE_URL="https://ellm.nrp-nautilus.io/anthropic"
export ANTHROPIC_MODEL="${AUDIT_MODEL:-qwen3}"
export AUDIT_MODEL="$ANTHROPIC_MODEL"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export ENABLE_TOOL_SEARCH=false
if [[ "${1:-}" == "--audit" ]]; then
  shift
  exec python agent/audit.py "$@"
fi
exec "${CLAUDE_BIN:-claude}" --model "$ANTHROPIC_MODEL" "$@"
