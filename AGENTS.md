# AGENTS — Working Guidelines for Coding Agents

This repository welcomes help from coding agents. This document lays out
how to work here effectively and safely, with minimal friction.


## Project Snapshot
- App: Terminal UI (Textual) that blends shell, simple `sam`-style edits,
  and AI chat (Anthropic Claude) into a single tool called "conch".
- Key modules: `conch.tui`, `conch.commands`, `conch.sam`, `conch.files`,
  `conch.cas`, `conch.anthropic`.
- Entrypoint for users: `conch` (via `pyproject` script) or `python main.py`.
- CI: GitHub Action at `.github/workflows/ci.yml` runs tests with `uv`.


## Quick Start (use uv)
- Install/resolve deps (incl. dev):
  - `uv sync --group dev`
- Run tests:
  - `uv run pytest -q`
- Smoke run (non-interactive):
  - `uv run python main.py --test`  # starts TUI and auto-exits
- Launch TUI (interactive):
  - Ensure `keyfile` env var points to a file containing your Anthropic API key
  - `uv run python main.py`

Environment variables:
- `keyfile`: Path to a file containing the Anthropic API key (required for AI mode).
- `CONCH_CAS_ROOT`: Optional override for content-addressed storage root
  (default: `~/.conch/cas`).


## Code Formatting
- Formatter: Black is the standard.
- Check formatting:
  - `uv run black --check .`
- Apply formatting:
  - `uv run black .`
- Alternate (no env activation needed):
  - `uvx black --check .`
  - `uvx black .`


## Repository Conventions
- Keep changes focused: fix the task at hand without broad refactors.
- Maintain style: follow existing code patterns; prefer readable names over single letters.
- Tests first (when possible): prioritize adding or updating tests that target the change.
- Don’t add license headers or modify licensing.
- Don’t commit changes here automatically. OpenAI’s Codex CLI typically uses
  patch-based edits; maintainers will commit.


## Agent Workflow
1. Plan
   - For multi-step work, outline a short plan.
   - Keep steps crisp (5–7 words each). Maintain exactly one `in_progress` step.
2. Explore
   - Prefer `rg` (ripgrep) for searching files.
   - Read files in ≤250-line chunks to avoid truncation.
3. Implement
   - Use patch-based edits (apply patches in-place; no new tooling required).
   - Update docs/tests as needed by your change.
4. Validate
   - Run tests with `uv run pytest -q`.
   - For the TUI, a smoke run is `uv run python main.py --test`.
5. Hand off
   - Summarize what changed and any follow-ups. Offer to extend CI or docs if useful.


## Testing Guidance
- Run: `uv sync --group dev && uv run pytest -q`.
- Scope: favor targeted tests close to changed logic.
- Avoid network in tests: the suite should not require the Anthropic API.
- If you need to exercise AI paths interactively, set `keyfile` locally —
  never check secrets into the repo.


## Textual/TUI Notes
- The TUI uses `RichLog` via `LogView` for performance.
- Modes: `sh` (shell), `ed` (sam), `ai` (Anthropic). Toggle with F9.
- Useful commands in the input box:
  - `:help` — show help
  - `!ls -la` — run a shell command
  - `< README.md` — load file into the log
  - `< src` — list a directory
  - `:gf` — open file at the current cursor (dot)
  - `:w` — write the current log buffer to CAS (prints the hash)
- Cursor ("dot") navigation: Up/Down arrows move; Shift+Up/Down adjusts selection.


## `sam` Subset (editing semantics)
Supported operations (addressed, 1-based):
- `a`, `c`, `d`, `i`, `m`, `q`, `s`, `t`, and `.` (move dot)
- Parser and executor live in `conch.sam`; raise `SamParseError` for errors.


## Content Addressed Storage (CAS)
- Location: `conch.cas` (SHA-256 of UTF-8 content).
- Size guard: rejects content > 4 MB.
- API: `CAS.put(str) -> hash`, `CAS.get(hash) -> str|None`, `CAS.pin(hash)`.
- CLI demo: `python src/scripts/cas_demo.py` (creates a temp CAS root).


## Security & Secrets
- The only secret is the Anthropic API key (read from the path in `keyfile`).
- Do not log keys or persist them anywhere except the user’s chosen file.
- Tests and CI must not depend on external networks or real keys.


## CI
- Defined in `.github/workflows/ci.yml`:
  - Checks out code, sets up Python 3.12 and `uv`, syncs deps (dev group), runs tests.
- If you add linting or packaging checks, keep them fast and deterministic.


## Common Tasks for Agents
- Add a slash/colon command: implement in `conch.commands` and wire from `conch.tui`.
- Extend `sam` behavior: add tests in `tests/test_sam*.py` and update `conch.sam`.
- Improve file handling: add tests in `tests/test_fs.py`, modify `conch.files`.
- Tweak AI handling: `conch.anthropic` is the async client; handle errors gracefully in the TUI.


## Don’ts
- Don’t introduce unrelated refactors with feature fixes.
- Don’t leak secrets or add telemetry that uploads data by default.
- Don’t rely on platform-specific features; tests run on Linux in CI.


## Questions
If something is ambiguous, prefer:
- Adding a concise test that expresses the desired behavior; or
- Leaving a short TODO note and opening an issue/PR comment summarizing options.


## Pitch Methodology
Each pitch is a small, end‑to‑end slice of work tracked in the devlog.

- Start: Create a new devlog entry `devlog/YYYY-MM-DD-<topic>.md` with Summary, Goals, Actions, Artifacts, Repro, Next Steps.
- Goals: State measurable goals and how you will verify them (tests, CI, docs updated).
- Develop: Make focused patches; keep scope tight; update/add tests alongside code.
- Test: Run `uv run pytest -q`; avoid networked tests; keep CI deterministic.
- Integrate: Adjust CI as needed (e.g., add steps, pin Python); keep it fast.
- Document: Update `README.md`, `AGENTS.md`, or in‑app help as relevant; record commands and rationale in the devlog.
- Wrap up: Run formatter (`uv run black .` or `uvx black .`), update the devlog with outcomes, and do a final commit.
  - Typical commit message: `pitch: <topic> — <short summary>`.
  - Note: In Codex CLI, agents usually don’t commit; maintainers handle the actual commit/merge.

### Pitch Template
- Template file: `devlog/pitch-template.md`
- Create a new entry from the template:
  - `cp devlog/pitch-template.md "devlog/$(date +%F)-<topic>.md"`
  - Fill in placeholders for date/topic and sections.
