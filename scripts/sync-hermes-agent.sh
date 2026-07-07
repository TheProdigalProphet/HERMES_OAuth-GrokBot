#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f manifest.json ]]; then
  echo "Error: manifest.json not found in repository root."
  exit 1
fi

if [[ -n "${1:-}" ]]; then
  endpoint="$1"
elif [[ -n "${HERMES_URL:-}" ]]; then
  endpoint="$HERMES_URL"
elif [[ -n "${HERMES_BASE_URLS:-}" ]]; then
  endpoint="${HERMES_BASE_URLS%%,*}"
else
  endpoint="http://127.0.0.1:8000"
fi

if [[ -n "${HERMES_AGENT_CLI:-}" ]]; then
  cli="$HERMES_AGENT_CLI"
elif command -v hermes-agent >/dev/null 2>&1; then
  cli="hermes-agent"
elif command -v hermes >/dev/null 2>&1; then
  cli="hermes"
else
  echo "No Hermes Agent CLI found."
  echo "Install your Hermes Agent CLI or set HERMES_AGENT_CLI to the executable name."
  echo "Suggested command: hermes-agent sync manifest.json --endpoint $endpoint"
  exit 1
fi

echo "Running Hermes Agent sync command: $cli sync manifest.json --endpoint $endpoint"
"$cli" sync manifest.json --endpoint "$endpoint"
