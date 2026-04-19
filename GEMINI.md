# Gemini CLI — imdbapi submodule

This is **`imdbapi-client`** (`backend/chain/imdbapi/`) — part of the Movie Finder project.
GitHub repo: `aharbii/imdbapi-client` · Parent repo: `aharbii/movie-finder`

> See root GEMINI.md for: full submodule map, GitHub issue/PR hygiene, coding standards, branching strategy, session start protocol.

---

## What this submodule does

Async Python client for [imdbapi.dev](https://imdbapi.dev).

- **HTTP:** `httpx` (async)
- **Validation:** Pydantic v2
- **Resilience:** `tenacity` retries
- **Lifecycle:** Standalone `uv` project with its own `uv.lock`.

---

## Design patterns

- **Adapter pattern:** Wraps raw REST responses into domain types.
- **Resilience:** Exponential back-off (Issue #8: coordinate delay changes with SSE).
- **PEP 695:** Modern type parameter syntax for Python 3.13.

---

## Coding standards (imdbapi-specific)

- No raw `dict` returned — use Pydantic models.
- Catch specific exceptions: `httpx.HTTPStatusError`, `httpx.RequestError`, `tenacity.RetryError`.

---

## VS Code setup

`backend/chain/imdbapi/.vscode/` — full workspace configuration for imdbapi only.

- Interpreter: `/opt/venv/bin/python` inside the attached `imdbapi` container
- Start the editor container with `make editor-up`, then attach via VS Code Dev Containers
- `launch.json`: `main.py` interactive runner + pytest all/current file from the container
- `tasks.json`: host-side `make ...` wrappers for build, editor attach, lint, test, coverage, and pre-commit

---

## Workflow invariants (imdbapi-specific)

- Gitlink path is `imdbapi` inside `aharbii/movie-finder-backend`. Parent path filters must use `imdbapi`, not `imdbapi/**`.
- Retry or timeout changes must be flagged to `chain/` — they affect the SSE stream budget.

### Submodule pointer bump

```bash
git add imdbapi && git commit -m "chore(imdbapi): bump to latest main"   # in backend/
git add backend && git commit -m "chore(backend): bump to latest main"   # in root
```
