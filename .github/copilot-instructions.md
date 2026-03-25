# GitHub Copilot — imdbapi-client

Async IMDb REST client for Movie Finder. Wraps the external IMDb API, handles retries,
and maps raw responses to internal domain types. Used by the `chain/` LangGraph pipeline.

Parent project: `aharbii/movie-finder` — all issues created there first, then linked here.

---

## Package role

- Async HTTP client (httpx) for IMDb API
- Retry logic with exponential back-off and rate-limit handling (429)
- Maps raw IMDb JSON responses → internal `Movie` domain types
- Callers never see raw HTTP responses — all data goes through the adapter layer

---

## Python standards

- Python 3.13, `uv` workspace member (`backend/.venv`), `ruff` + `mypy --strict`, line length **100**
- Type annotations required on all public functions
- Async all the way — no blocking I/O in async context
- Docstrings on all public classes and functions (Google style)
- Tests: `pytest` with `respx` for HTTP-level mocking. No real IMDb API calls in tests.

---

## Design patterns — follow these

| Pattern | Rule |
|---|---|
| **Adapter** | Client wraps the external IMDb API and maps to internal domain types. Callers never see raw HTTP. |
| **Configuration object** | All env vars (API key, base URL, timeouts, retry config) loaded once in `config.py` via Pydantic `BaseSettings`. |

---

## Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

Hooks: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-merge-conflict`,
`detect-private-key`, `detect-secrets`, `pretty-format-json`, `sort-simple-yaml`,
`mypy --strict`, `ruff-check --fix`, `ruff-format`.

---

## Known issues most relevant to this package

| # | Title |
|---|---|
| #8 | IMDb retry base delay 30 s — blocks SSE stream |
| #16 | IMDb stagger delay adds artificial latency |

---

## Cross-cutting — check for every change

1. GitHub issue in `aharbii/movie-finder` + this repo (linked)
2. Branch: `feature/`, `fix/`, `chore/` (kebab-case)
3. ADR if IMDb API contract or retry strategy changes
4. `.env.example` updated in imdbapi + backend + root
5. `backend/chain/` assessed — this client is called directly from the `imdb_fetch` node
6. PlantUML `09-seq-langgraph-execution.puml` updated for timing/retry changes
