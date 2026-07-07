#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_URL="${1:-${HERMES_URL:-http://127.0.0.1:8000}}"
BACKEND_LOG="${HERMES_BACKEND_LOG:-/tmp/hermes_backend.log}"
BACKEND_PID_FILE="${HERMES_BACKEND_PID_FILE:-/tmp/hermes_backend.pid}"
BACKEND_PID=""

export HERMES_AGENT_CLI="${HERMES_AGENT_CLI:-hermes-agent}"
export HERMES_BASE_URLS="${HERMES_BASE_URLS:-$HERMES_URL}"

cleanup_on_error() {
  local exit_code=$?
  trap - EXIT
  if (( exit_code != 0 )) && [[ -n "$BACKEND_PID" ]]; then
    echo "Stopping FastAPI backend..."
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  exit "$exit_code"
}

trap cleanup_on_error EXIT

cd "$REPO_ROOT"

if [[ ! -f requirements.txt ]]; then
  echo "Error: requirements.txt not found in repository root."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install it with: sudo apt update && sudo apt install python3 python3-venv python3-pip"
  exit 1
fi

if [[ ! -d .venv ]] || [[ ! -f .venv/bin/activate ]]; then
  if [[ -d .venv ]] && [[ ! -f .venv/bin/activate ]]; then
    echo "Existing .venv is not a Linux-compatible virtual environment. Recreating it for WSL..."
    rm -rf .venv
  fi

  echo "Initializing Linux-compatible virtual environment..."
  python3 -m venv .venv

  if [[ ! -f .venv/bin/activate ]]; then
    echo "Error: WSL virtual environment activation script not found."
    exit 1
  fi

  source .venv/bin/activate
  python3 -m pip install --upgrade pip
  python3 -m pip install -r requirements.txt
else
  source .venv/bin/activate
fi

echo "Starting FastAPI Backend..."
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

echo "Waiting for health check..."
for _ in {1..30}; do
  if curl -fsS "$HERMES_URL/health" > /dev/null; then
    break
  fi

  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend exited before becoming healthy."
    tail -n 20 "$BACKEND_LOG" || true
    exit 1
  fi

  sleep 2
done

if ! curl -fsS "$HERMES_URL/health" > /dev/null; then
  echo "Timed out waiting for backend health at $HERMES_URL/health"
  tail -n 20 "$BACKEND_LOG" || true
  exit 1
fi

if [[ -f manifest.json ]]; then
  echo "Synchronizing manifest with Hermes Agent..."
  ./scripts/sync-hermes-agent.sh "$HERMES_URL"
else
  echo "Critical Error: manifest.json not found."
  exit 1
fi

echo "Publishing persona documents (Librarian, Expert Dev)..."
./scripts/publish-personas-wsl.sh "$HERMES_URL"

trap - EXIT
echo "Sync complete. Backend running on PID: $BACKEND_PID"
echo "Backend log: $BACKEND_LOG"
echo "PID file: $BACKEND_PID_FILE"
echo "You can now run Streamlit via: ./scripts/run-streamlit-nohup.sh"
