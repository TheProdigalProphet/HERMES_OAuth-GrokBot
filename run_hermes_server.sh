#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -f requirements.txt ]]; then
  echo "Error: requirements.txt not found in repository root."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install it with: sudo apt update && sudo apt install python3 python3-venv python3-pip"
  exit 1
fi

if [[ -d .venv && ! -f .venv/bin/activate ]]; then
  echo "Existing .venv is not a Linux-compatible virtual environment. Recreating it for WSL..."
  rm -rf .venv
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

if [[ ! -f .venv/bin/activate ]]; then
  echo "Error: WSL virtual environment activation script not found."
  exit 1
fi

source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [[ -z "${HERMES_AGENT_CLI:-}" ]]; then
  if command -v hermes-agent >/dev/null 2>&1; then
    export HERMES_AGENT_CLI=hermes-agent
  elif command -v hermes >/dev/null 2>&1; then
    export HERMES_AGENT_CLI=hermes
  fi
fi

if [[ -z "${HERMES_AGENT_CLI:-}" ]]; then
  echo "Warning: Hermes CLI not found. Set HERMES_AGENT_CLI if your binary is named differently."
fi

echo "Starting FastAPI app..."
uvicorn src.api.main:app --reload &
APP_PID=$!

trap 'echo "Stopping FastAPI app..."; kill "$APP_PID" 2>/dev/null || true; exit' INT TERM EXIT

sleep 2

if [[ -n "${HERMES_AGENT_CLI:-}" ]]; then
  echo "Syncing Hermes Agent manifest..."
  "$HERMES_AGENT_CLI" sync manifest.json --endpoint http://127.0.0.1:8000
else
  echo "Skipping Hermes sync because HERMES_AGENT_CLI is not set."
  echo "You can run: export HERMES_AGENT_CLI=hermes-agent"
fi

echo "Hermes WSL helper complete. Press Ctrl+C to stop the FastAPI app."
wait "$APP_PID"
