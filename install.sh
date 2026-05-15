#!/usr/bin/env bash
# install.sh — Install twat-llm locally
# LLM integration for twat
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing twat-llm..."
uv pip install -e . 2>/dev/null || pip install -e .
echo "Done."
