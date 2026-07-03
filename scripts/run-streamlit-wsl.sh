#!/bin/bash

# run-streamlit-wsl.sh
# Start the Streamlit Hermes Gematria Oracle on WSL
# Usage: ./run-streamlit-wsl.sh [HERMES_URL]
# Example: ./run-streamlit-wsl.sh http://127.0.0.1:8000

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_URL="${1:-http://127.0.0.1:8000}"

echo "===== Streamlit Hermes Gematria Oracle ====="
echo "Repository: $REPO_ROOT"
echo "Hermes Backend: $HERMES_URL"
echo ""

cd "$REPO_ROOT"

echo "Step 1: Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

echo "Step 2: Activating virtual environment..."
source .venv/bin/activate

echo "Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -q -r requirements.txt

echo "Step 4: Starting Streamlit app..."
echo "App will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop."
echo ""

export HERMES_BASE_URLS="$HERMES_URL"
streamlit run streamlit_gematria_hermes.py --server.address=127.0.0.1 --server.port=8501
