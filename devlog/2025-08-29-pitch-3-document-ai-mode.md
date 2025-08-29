## 2025-08-29 — Pitch 3: Document AI Mode

### Status
- Done (2025-08-29)

### Summary
Clarify and surface AI mode usage. Visibly show the currently selected provider/model in the TUI, and provide clear instructions for switching and configuring Anthropic and OpenAI models.

### Goals
- [ ] Show current provider:model in the TUI at all times.
- [ ] Update in-app help to include Anthropic and OpenAI instructions with examples.
- [ ] Add README section for AI Mode setup and usage (env vars, :use syntax, examples).

### Acceptance Criteria
- TUI displays the active selection as `provider:model` (e.g., `anthropic:claude-3-haiku-20240307` or `openai:gpt-4o-mini`).
- After running `:use provider:model`, the display updates immediately.
- `:help` output includes: how to select models for both Anthropic and OpenAI, and which env vars to set.
- README has a dedicated “AI Mode” section covering keys and examples for both providers.

### Out of Scope
- Streaming responses, function calling, tool use, or additional providers.
- Persisting model selection across runs (can be a future pitch).

### Open Questions
- Placement: Border title vs. a dedicated status line? (Default proposal: include in border title, e.g., `Conch [anthropic:claude-3-haiku-20240307]`.)
- Do we want a `:model` (or `:status`) command that prints the current provider:model explicitly?

### Actions (Development Phase)
- Update TUI to display current `provider:model` in the border title.
- Ensure `:use` triggers a UI refresh of the display.
- Add `:model` command to print current selection.
- Expand `HELP_TEXT` with provider/model selection and key env vars.
- Update README with Providers & Models notes and examples.
- Tests: verify help text contains provider guidance; verify title formatting via unit test.

### Artifacts
- Code: `src/conch/tui.py` (UI display), `src/conch/commands.py` (ensure logging/refresh)
- Docs: `README.md` (AI Mode), in‑app help text
- Tests: `tests/test_help_text.py` (expand), potential small TUI display test

### Repro
- Setup: `uv sync --group dev`
- Tests: `uv run pytest -q`
- App (smoke): `uv run python main.py --test`

### Wrap-up
- Formatting: `uv run black .` (or `uvx black .`)
- Tests: 37 passed
- Outcome: Title shows `[provider:model]`; `:model` prints current selection; help + README updated
- Commit suggestion: `pitch: document-ai-mode — show current model; docs for Anthropic/OpenAI`
