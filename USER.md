# USER — How to Get the Best from This Repo + Agent

This guide summarizes how to work with the agent (and this repo) so we move fast with clarity and minimal surprises.

## Requests
- Be explicit: desired outcome, constraints, and a clear “definition of done”.
- Provide an example: a tiny input→output sample accelerates alignment.
- Timebox scope: “Do X only; leave Y/Z for later” to avoid overshooting.
- Call out risk areas: files or APIs that should not change.

## Pitches (preferred workflow)
- Use the devlog pitch template to open a pitch (Status: Proposed).
- Write Goals and Acceptance Criteria; add Out‑of‑Scope and Open Questions.
- Wait for alignment: mark Status: Agreed (date/initials) before coding.
- Keep pitches small and end‑to‑end; track actions and outcomes in the devlog.

## Environment & Permissions
- Say which tools to use (e.g., “use uv”, “ok to install dev deps”).
- Mention sandbox/approval mode and network policy up front.
- Share secrets location conventions (e.g., `keyfile`, `OPENAI_API_KEY`). Never paste secrets into chats.

## Decisions & Planning
- Prefer small, reversible steps; ask for a plan for multi‑phase work.
- If you want alternatives first, request a brief trade‑off comparison.
- Call out priorities so I can sequence tasks accordingly.

## Validation
- Specify commands to run locally: `uv sync --group dev`, `uv run pytest -q`.
- Point to critical tests or behaviors you care most about.
- Ask for a short demo snippet only when useful; we avoid noise.

## Docs & CI
- When UX/behavior changes, ask to update both README and in‑app help.
- Confirm up front whether to add CI checks (Black, lint, packaging).

## Security & Data
- Clarify what’s allowed: telemetry, external calls, and file writes.
- Provide dummy keys for tests; avoid real network in the test suite.
- Keep secrets in files referenced by env vars; not in the repo.

## Change Control
- Tell me whether to commit or leave changes staged.
- If you want a PR, specify branch naming and commit message style.

## When I’m Stuck
- Invite a pause and options: “If blocked, propose 2 approaches.”

## Quick Pitch Template (pasteable)
- Pitch: <topic> (Proposed)
- Goals: <bullets>
- Acceptance: <bullets>
- Out‑of‑scope: <bullets>
- Constraints: <sandbox/approvals/network>
- Validation: `uv run pytest -q`; other checks?
- Deliverables: code, tests, docs, CI?
- Commit/PR: <preferences>

