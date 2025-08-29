## 2025-08-29 — Pitch: GPT‑5 max-completion-tokens

### Status
- Done (2025-08-29 rb)

### Summary
- Address GitHub issue #21 by updating the OpenAI client to send `max-completion-tokens` when targeting GPT‑5 models, while preserving `max_tokens` for other models. Added targeted tests to verify the request payload without network access.

### Goals
- [x] Detect GPT‑5 model names and switch to `max-completion-tokens`.
- [x] Preserve existing behavior (`max_tokens`) for non‑GPT‑5 models.
- [x] Add unit tests that validate the exact JSON sent.

### Acceptance Criteria
- When `model` starts with `gpt-5`, outgoing JSON includes `"max-completion-tokens": <n>` and excludes `max_tokens`.
- For other models (e.g., `gpt-4o-mini`), outgoing JSON includes `"max_tokens": <n>` and excludes `max-completion-tokens`.
- Tests pass for these cases without real network calls.

### Out of Scope
- Broader refactors of the TUI or AI provider selection.
- Changes to Anthropic client behavior.
- Stabilizing unrelated `LogView` headless vs. mounted rendering differences.

### Open Questions
- None for this slice; behavior is unambiguous per issue #21.

### Actions (Development Phase)
- Update `OpenAIClient.oneshot` to branch on `model.startswith("gpt-5")` and set the appropriate token key.
- Add `tests/test_openai_gpt5_tokens.py` with a monkeypatched `httpx.AsyncClient` to capture payloads.
- Run tests and apply Black formatting.

### Artifacts
- Code: `src/conch/openai_client.py`
- Tests: `tests/test_openai_gpt5_tokens.py`

### Repro
- Setup: `uv sync --group dev`
- Tests (targeted): `uv run pytest -q tests/test_openai_gpt5_tokens.py`
- Full suite: `uv run pytest -q`

### Notes
- The change preserves compatibility for existing OpenAI models and only toggles parameter naming for GPT‑5. If OpenAI expands the new parameter to other future families, we may generalize the detection.

### Wrap-up
- Formatting: `uv run black .`
- Outcomes: All new tests pass; GPT‑5 requests now use `max-completion-tokens` as required.
- Commit suggestion: `pitch: gpt5 — switch to max-completion-tokens for GPT‑5`

