#!/usr/bin/env bash
# Test for task 001 — Python lint stack
set -euo pipefail
cd /work

# (1) install dev deps
pip install -e ".[dev]" pre-commit >/dev/null

# (2) hooks installed
pre-commit install >/dev/null

# (3) all hooks pass on all files
pre-commit run --all-files

# (4) lint clean
ruff check src/
black --check src/

# (5) no nuclear bypasses
if grep -REn "# *noqa($|[^a-z])|# *fmt: *off" src/ ; then
  echo "FAIL: '# noqa' or '# fmt: off' found"
  exit 1
fi

echo "PASS task-001"
