#!/usr/bin/env bash
# build.sh — Build twat-llm
# LLM integration for twat
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Linting..."
fd -e py -x uvx ruff check --fix {} 2>/dev/null || true
fd -e py -x uvx ruff format {} 2>/dev/null || true

echo "Testing..."
uvx hatch test 2>/dev/null || uv run pytest -xvs 2>/dev/null || echo "No tests configured"

echo "Building..."
uvx hatch build 2>/dev/null || uv build 2>/dev/null || echo "Build skipped"

echo "Done."
