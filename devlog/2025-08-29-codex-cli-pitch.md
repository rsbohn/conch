# 2025-08-29 — Pitch 1: Codex CLI

## Summary
First Codex CLI pitch: validate the repo with `uv`, ensure tests pass, add CI, and document agent workflow.

## Actions
- Explained project structure and purpose for quick onboarding.
- Ran test suite with `uv`:
  - `uv sync --group dev`
  - `uv run pytest -q` → 34 passed
- Added CI workflow using `uv`:
  - `.github/workflows/ci.yml` runs on push/PR, syncs deps, runs tests.
- Wrote `AGENTS.md` with clear instructions for coding agents (setup, workflow, testing, CI, guardrails).
 - Added Black formatting check to CI and formatted the repo.
 - Updated `README.md` with Development and Black instructions.
 - Documented the Pitch methodology in `AGENTS.md` and added a reusable Pitch Template at `devlog/pitch-template.md`.

## Rationale
Demonstrate a complete, reproducible loop (explain → test → CI → docs) using Codex CLI, aligning with existing devlog patterns and keeping scope tight.

## Artifacts
- CI: `.github/workflows/ci.yml`
- Agent guide: `AGENTS.md`
 - Pitch template: `devlog/pitch-template.md`
 - README changes: Development + formatting section
 - Formatting: Repository formatted with Black (12 files)

## Repro
- Local: `uv sync --group dev && uv run pytest -q`
- Smoke: `uv run python main.py --test`

## Next Steps
- Optional: add linting with `ruff` to CI.
- Optional: packaging check (`uv build`) in CI.
 - Consider adding a Makefile with common `uv` commands.
