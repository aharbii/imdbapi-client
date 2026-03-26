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

## Workflow invariants

- This repo is the gitlink path `imdbapi` inside `aharbii/movie-finder-backend`. Parent
  workflow/path filters must use `imdbapi`, not `imdbapi/**`.
- Cross-repo tracker issues originate in `aharbii/movie-finder`. Create the linked child issue in
  this repo only if this repo will actually change.
- Inspect `.github/ISSUE_TEMPLATE/*.yml`, `.github/PULL_REQUEST_TEMPLATE.md` when present, and a
  recent example before creating or editing issues/PRs. Do not improvise titles or bodies.
- For child issues in this repo, use `.github/ISSUE_TEMPLATE/linked_task.yml` and keep the
  description, file references, and acceptance criteria repo-specific.
- If CI, required checks, or merge policy changes affect this repo, update contributor-facing docs
  here and in `aharbii/movie-finder-backend` and/or `aharbii/movie-finder` where relevant.
- If a new standalone issue appears mid-session, branch from `main` unless stacking is explicitly
  requested.
- PR descriptions must disclose the AI authoring tool + model. Any AI-assisted review comment or
  approval must also disclose the review tool + model.

---

## VSCode setup

`backend/imdbapi/.vscode/` — full workspace configuration for imdbapi only.
- Interpreter: `backend/.venv/bin/python` (`uv sync --all-packages` from `backend/`)
- `launch.json`: `main.py` interactive runner + pytest all/current file
- `tasks.json`: lint, test, pre-commit (commands run via `cd ..` to workspace root)
- Modifying configs: keep parity with `backend/.vscode/` aggregate tasks. Update `CLAUDE.md`,
  `GEMINI.md`, `AGENTS.md`, and the repo's `.github/copilot-instructions.md` after.
