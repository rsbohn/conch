# Short-term plan — next steps

Task receipt & plan: I'll propose a prioritized set of concrete next steps to stabilize, harden, and ship the Conch TUI; each item has a short rationale, rough effort estimate, and a quick verification step.

## Checklist (prioritized)

1. Add development dependencies and test runner (high)
   - Why: ensure a reproducible environment for contributors and CI.
   - Effort: 15–30m
   - What to add: `requirements-dev.txt` or `pyproject.toml` dev dependencies including `pytest` and `tox` (optional).
   - Verify: `uv run pytest tests` passes locally.

2. Continuous Integration (high)
   - Why: run tests, lint, and packaging checks on push/PR.
   - Effort: 30–60m
   - Action: add a GitHub Actions workflow that runs `uv run pytest tests`, `python -m pip install -e .`, and flake8/ruff.
   - Verify: green CI run on main branch or a test PR.

3. Add basic linting and formatting (medium)
   - Why: keep code consistent and catch simple bugs early.
   - Effort: 30–45m
   - Tools: `ruff` or `flake8` + `black` for formatting.
   - Verify: `uv run ruff check src tests` and `uv run black --check .`

4. Harden file/directory handling with tests (high)
   - Why: many edge cases (permissions, binary files, long paths) are IO-related.
   - Effort: 45–90m
   - Add tests for: permission-denied, binary detection (UnicodeDecodeError), very large files (streaming), and non-ASCII paths.
   - Verify: `pytest -q` covers new edge cases.

5. Add command history + navigation (medium)
   - Why: improved UX (arrow keys, history persisted optionally).
   - Effort: 2–4h
   - Approach: store last N commands in memory and (optionally) write to `~/.config/conch/history`.
   - Verify: up/down arrows cycle through recent commands.

6. Add syntax highlighting for files (nice-to-have)
   - Why: makes file viewing more useful.
   - Effort: 2–4h
   - Approach: integrate Pygments to render highlighted text into Rich markup, with a fallback to plain text.
   - Verify: open `README.md` shows highlighted markdown.

7. Packaging + minimal installer (medium)
   - Why: make it easy for others to install (pip editable / wheel).
   - Effort: 1–2h
   - Action: add proper `pyproject.toml` metadata (if missing) and tests for `python -m conch` entrypoint.
   - Verify: `pip install -e .` then `python -m conch` runs.

8. Improve logging and error telemetry (low)
   - Why: capture useful diagnostics for bug reports.
   - Effort: 1–2h
   - Action: add optional debug flag `--debug` to log exceptions to `~/.cache/conch/last-error.log`.
   - Verify: reproduce an exception and inspect the log file.

9. Document developer and contributor workflow (low)
   - Why: onboarding and reproducibility.
   - Effort: 30–60m
   - Add/update `README.md` sections: dev setup, run tests, run app, VS Code task usage.
   - Verify: follow README steps in a fresh environment.

10. UX polish: keyboard shortcuts and accessibility (ongoing)
    - Why: better usability across terminals and assistive tech.
    - Effort: iterative
    - Examples: add `Ctrl+H` for help, ensure color contrast, test in Windows Terminal / PowerShell / WSL.

## Quick quality gates
- Build: ensure `python -m pip install -e .` works (or `uv run python -m pip install -e .`).
- Lint/Format: run `uv run ruff` / `uv run black --check`.
- Tests: `uv run pytest tests` (runs existing tests).
- Smoke: `uv run python main.py --test` should start and exit cleanly.

## Useful commands
```powershell
# run tests
uv run pytest tests

# run the app in test mode (auto-exits)
uv run python main.py --test

# run a single test file
uv run pytest -q tests/test_directory_listing.py
```

## Short-term milestones (next 7 days)
- Day 1: Add dev deps, CI workflow, ensure tests run in CI.
- Day 2: Add linting, run and fix prioritized lints.
- Day 3–4: Add edge-case tests for IO and file handling.
- Day 5–7: Implement command history and basic syntax highlighting proof-of-concept.

If you'd like, I can start implementing any single item now (for example: create `requirements-dev.txt`, add a GitHub Actions workflow, or add history persistence). Which one should I pick first?
