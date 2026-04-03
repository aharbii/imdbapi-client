# OpenAI Codex CLI — imdbapi submodule

Foundational mandate for `imdbapi-client` (`backend/imdbapi/`).

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
- Interpreter: `/opt/venv/bin/python` inside the attached `imdbapi` container
- Start the editor container with `make editor-up`, then attach via VS Code Dev Containers
- `launch.json`: `main.py` interactive runner + pytest all/current file from the container
- `tasks.json`: host-side `make ...` wrappers for build, editor attach, lint, test, coverage, and pre-commit
- Modifying configs: keep parity with `backend/.vscode/` aggregate tasks. Update `CLAUDE.md`,
  `GEMINI.md`, `AGENTS.md`, and the repo's `.github/copilot-instructions.md` after.
