# GitHub Copilot — imdbapi-client

Async IMDb REST client for Movie Finder. Wraps the external IMDb API, handles retries,
and maps raw responses to internal domain types. Used by the `chain/` LangGraph pipeline.

This package is a **standalone uv project** with its own lifecycle and `uv.lock`.

Parent project: `aharbii/movie-finder` — all issues created there first, then linked here.

---

## Package role

- Async HTTP client (httpx) for IMDb API
- Retry logic with exponential back-off and rate-limit handling (429)
- Maps raw IMDb JSON responses → internal `Movie` domain types
- Callers never see raw HTTP responses — all data goes through the adapter layer

---

## Python standards

- Python 3.13, Docker-only local dev via `make` + `docker compose`, `ruff` + `mypy --strict`, line length **100**
- Type annotations required on all public functions
- Async all the way — no blocking I/O in async context
- Docstrings on all public classes and functions (Google style)
- Tests: `pytest` with `respx` for HTTP-level mocking. No real IMDb API calls in tests.

---

## Design patterns — follow these

| Pattern                  | Rule                                                                                                             |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **Adapter**              | Client wraps the external IMDb API and maps to internal domain types. Callers never see raw HTTP.                |
| **Configuration object** | All env vars (API key, base URL, timeouts, retry config) loaded once in `config.py` via Pydantic `BaseSettings`. |
| **PEP 695**              | Modern type parameter syntax for Python 3.13.                                                                    |

---

## Pre-commit hooks

```bash
make pre-commit
```

Hooks: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-merge-conflict`,
`detect-private-key`, `detect-secrets`, `pretty-format-json`, `sort-simple-yaml`,
`mypy --strict`, `ruff-check --fix`, `ruff-format`.

---

## Known issues most relevant to this package

| #   | Title                                          |
| --- | ---------------------------------------------- |
| #8  | IMDb retry base delay 30 s — blocks SSE stream |
| #16 | IMDb stagger delay adds artificial latency     |

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

## Cross-cutting — check for every change

1. GitHub issue in `aharbii/movie-finder` + linked child issue here only if this repo changes, using the current templates and recent examples
2. Branch: `feature/`, `fix/`, `chore/` (kebab-case) from `main` unless stacking is explicitly requested
3. ADR if IMDb API contract or retry strategy changes
4. `.env.example` updated in imdbapi + backend + root
5. `backend/chain/` assessed — this client is called directly from the `imdb_fetch` node
6. PlantUML `09-seq-langgraph-execution.puml` updated for timing/retry changes
