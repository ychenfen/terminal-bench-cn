# Task 001 — Add ruff + black + pre-commit to a new Python project

## Context
You receive an empty Python project skeleton (only `pyproject.toml` and `src/app/__init__.py`).
Configure code-quality tooling per team policy.

## Acceptance criteria
1. `ruff` and `black` installed as dev dependencies under `[project.optional-dependencies] dev`
2. A working `.pre-commit-config.yaml` at the repo root with at least the ruff and black hooks
3. `pre-commit run --all-files` passes
4. `ruff check src/` and `black --check src/` pass
5. Bypassing via `# noqa` or `# fmt: off` is forbidden

## Input
Initial repo state lives in Docker image `task-001:base`, working dir `/work`.

## Test
`tests/test_001.sh` runs:
```
cd /work
pip install -e ".[dev]" pre-commit
pre-commit install
pre-commit run --all-files
ruff check src/
black --check src/
```
All exit codes must be 0.

## Hints (visible to the agent)
- Recommended ruff `select = ["E", "F", "I", "B"]`
- Line length ≤ 100 recommended
