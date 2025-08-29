# 2025-08-29 — Pitch 2: OpenAI Models

## Summary
Add OpenAI provider support alongside Anthropic: select provider via `:use`, route prompts accordingly, and document usage. Keep tests network-free.

## Goals
- [x] Implement OpenAI client with async `oneshot(prompt, model)` using `httpx`.
- [x] Allow `:use openai:<model>` to switch provider and model.
- [x] Update TUI to instantiate the correct client by provider.
- [x] Add tests for `:use openai:...` path (no network calls).
- [x] Document provider usage and keys.

## Actions
- Add `src/conch/openai_client.py` with `OpenAIClient` and `get_openai_key()`.
- Extend `:use` in `conch.commands` to parse `provider:model` and reset client.
- Update `conch.tui` to select `OpenAIClient` when `ai_provider == "openai"`.
- Add `tests/test_use_openai_model_command.py` mirroring Anthropic test.
- Update README with Providers & Models section (Anthropic/OpenAI).

## Artifacts
- Code: `src/conch/openai_client.py`, `src/conch/commands.py`, `src/conch/tui.py`
- Tests: `tests/test_use_openai_model_command.py`
- Docs: `README.md` Providers & Models section

## Repro
- `uv sync --group dev`
- `uv run pytest -q`

## Wrap-up
- Format: `uv run black .`
- Status: Tests pass locally.
- Commit: `pitch: openai-models — add OpenAI provider + :use support`
