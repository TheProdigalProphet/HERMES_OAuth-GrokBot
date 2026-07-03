#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f manifest.json ]]; then
  echo "Error: manifest.json not found in repository root."
  exit 1
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
  echo "Suggested command: hermes-agent sync manifest.json --endpoint http://127.0.0.1:8000"
  exit 1
fi

sync_command="$cli sync manifest.json --endpoint http://127.0.0.1:8000"
echo "Running Hermes Agent sync command: $sync_command"
eval "$sync_command"
