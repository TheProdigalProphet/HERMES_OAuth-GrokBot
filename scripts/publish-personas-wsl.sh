#!/usr/bin/env bash

# publish-personas-wsl.sh
# Publish all local agent personas into a running Hermes backend on WSL
# Usage: ./publish-personas-wsl.sh [HERMES_URL]
# Example: ./publish-personas-wsl.sh http://127.0.0.1:8000

HERMES_URL="${1:-http://127.0.0.1:8000}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKGROUND_DIR="$REPO_ROOT/data/background"

echo "===== Publishing Agent Personas to Hermes ====="
echo "Hermes Backend: $HERMES_URL"
echo "Background Directory: $BACKGROUND_DIR"
echo ""

if [ ! -d "$BACKGROUND_DIR" ]; then
    echo "Error: Background directory not found at $BACKGROUND_DIR"
    exit 1
fi

count=0
for persona_file in "$BACKGROUND_DIR"/*.json; do
    if [ -f "$persona_file" ]; then
        filename=$(basename "$persona_file")
        echo "Publishing: $filename"

        response=$(curl -s -X POST "$HERMES_URL/background/document" \
            -H "Content-Type: application/json" \
            -d @"$persona_file")

        if echo "$response" | grep -q '"id"'; then
            echo "  ✓ Success"
            ((count++))
        else
            echo "  ✗ Failed: $response"
        fi
    fi
done

echo ""
echo "Published $count persona(s)"
echo ""
echo "Next steps:"
echo "  1. Click 'Load background docs' in Hermes"
echo "  2. Click 'Sync profile' to integrate personas"
echo "  3. Personas are now available for agent reasoning"
