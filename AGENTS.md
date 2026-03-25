# OpenAI Codex CLI — imdbapi submodule

Foundational mandate for `imdbapi-client` (`backend/imdbapi/`).

---

## What this submodule does
Async Python client for [imdbapi.dev](https://imdbapi.dev).
- **HTTP:** `httpx` (async)
- **Validation:** Pydantic v2
- **Resilience:** `tenacity` retries

---

## Design patterns
- **Adapter pattern:** Wraps raw REST responses into domain types.
- **Resilience:** Exponential back-off (Issue #8: coordinate delay changes with SSE).

---

## Coding standards
- `mypy --strict` passes.
- No raw `dict` returned — use Pydantic models.
- Async all the way.

---

## VSCode setup

`backend/imdbapi/.vscode/` — full workspace configuration for imdbapi only.
- Interpreter: `backend/.venv/bin/python` (`uv sync --all-packages` from `backend/`)
- `launch.json`: `main.py` interactive runner + pytest all/current file
- `tasks.json`: lint, test, pre-commit (commands run via `cd ..` to workspace root)
- Modifying configs: keep parity with `backend/.vscode/` aggregate tasks. Update `CLAUDE.md`,
  `GEMINI.md`, `AGENTS.md`, and the repo's `.github/copilot-instructions.md` after.
