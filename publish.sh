#!/usr/bin/env bash
# publish.sh — Build and publish to PyPI using hatch-vcs semver from git tags.
# Order: clean → tidy (pre-commit autofixes, then commit them) → bump tag → build → publish.
# Tidying upfront keeps gitnextver's atomic commit from tripping the pre-commit hook.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

uvx hatch clean

if [[ -f .pre-commit-config.yaml ]] && command -v pre-commit >/dev/null 2>&1; then
    pre-commit run --all-files || true
fi
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "chore: pre-publish tidy" || true
fi

uvx gitnextver .
uvx hatch build
uv publish
