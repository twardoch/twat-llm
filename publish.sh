#!/usr/bin/env bash
# publish.sh — Build, install, and publish twat-llm to PyPI
# LLM integration for twat
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

bash "$SCRIPT_DIR/build.sh"
bash "$SCRIPT_DIR/install.sh"

echo "Tagging next version..."
uvx gitnextver@latest

echo "Publishing to PyPI..."
uvx hatch build
uv publish

echo "Done."
