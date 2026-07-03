#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if ! command -v streamlit >/dev/null 2>&1; then
  echo "Error: streamlit is not installed in the current environment."
  exit 1
fi

LOG_FILE="/tmp/streamlit_hermes.log"
PID_FILE="/tmp/streamlit_hermes.pid"

nohup streamlit run "$ROOT_DIR/../streamlit_gematria_hermes.py" \
  --server.address=127.0.0.1 \
  --server.port=8501 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=true \
  > "$LOG_FILE" 2>&1 &

STREAMLIT_PID=$!
echo "$STREAMLIT_PID" > "$PID_FILE"
echo "Streamlit started with PID $STREAMLIT_PID"
echo "Log file: $LOG_FILE"
echo "PID file: $PID_FILE"

echo "Waiting 3 seconds for startup..."
sleep 3

echo "--- tail of log ---"
tail -n 20 "$LOG_FILE"
