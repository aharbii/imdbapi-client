# Claude Code — imdbapi submodule

This is **`imdbapi-client`** (`backend/imdbapi/`) — part of the Movie Finder project.
GitHub repo: `aharbii/imdbapi-client` · Parent repo: `aharbii/movie-finder`

---

## What this submodule does

Production-ready async Python client for the [imdbapi.dev](https://imdbapi.dev) REST API.
Used by the LangGraph `enrich_imdb` node to enrich movie candidates with live IMDb metadata.

- **HTTP:** `httpx` (async, connection pooling)
- **Validation:** Pydantic v2 (response parsing, camelCase → snake_case mapping)
- **Resilience:** `tenacity` exponential back-off retries (base delay currently 30 s — issue #8)
- **Auth:** imdbapi.dev requires no authentication key
- **uv workspace member** of `backend/`

---

## Full project context

### Submodule map

| Path | GitHub repo | Role |
|---|---|---|
| `.` (root) | `aharbii/movie-finder` | Parent — all cross-repo issues |
| `backend/` | `aharbii/movie-finder-backend` | FastAPI + uv workspace root |
| `backend/app/` | (nested in backend) | FastAPI application layer |
| `backend/chain/` | `aharbii/movie-finder-chain` | LangGraph 8-node AI pipeline |
| `backend/imdbapi/` | `aharbii/imdbapi-client` | **← you are here** |
| `backend/rag_ingestion/` | `aharbii/movie-finder-rag` | Offline embedding ingestion |
| `frontend/` | `aharbii/movie-finder-frontend` | Angular 21 SPA |
| `docs/` | `aharbii/movie-finder-docs` | MkDocs documentation |
| `infrastructure/` | `aharbii/movie-finder-infrastructure` | IaC / Azure provisioning |

### Technology stack

| Layer | Stack |
|---|---|
| Language | Python 3.13, uv workspace member |
| HTTP | `httpx` (async) |
| Retry | `tenacity` (exponential back-off) |
| Validation | Pydantic v2 |
| Linting | `ruff` (line-length 100) · `mypy --strict` |
| Tests | `pytest --asyncio-mode=auto` |
| CI | Jenkins Multibranch |

### Environment variables

`imdbapi.dev` requires no API key. Optional (for examples only):
```
OPENAI_API_KEY, ANTHROPIC_API_KEY   # used only in examples/langchain_agent_example.py
```

---

## Design patterns to follow

| Pattern | Where | Rule |
|---|---|---|
| **Adapter** | The entire client | Wraps `imdbapi.dev` REST responses and maps them to internal domain types. Callers (chain nodes) never see raw HTTP responses or camelCase fields. |
| **Configuration object** | `config.py` / Pydantic `BaseSettings` | Retry settings, timeouts, base URL loaded from config — not hardcoded. |
| **Resilience decorator** | `tenacity` retry logic | Retry policy is applied at the transport layer, not inside business logic. New endpoints inherit the policy automatically. |

**Known issue #8:** The 30-second retry base delay blocks the SSE stream. Any retry policy change must be coordinated with the `chain/` team to verify the SSE timeout budget.

---

## Coding standards

- `mypy --strict` must pass — all public functions fully typed
- Pydantic models validate every field — no raw `dict` returned to callers
- No `type: ignore` without an explanatory comment
- No bare `except:` — catch `httpx.HTTPStatusError`, `httpx.RequestError`, `tenacity.RetryError`
- Docstrings on all public classes and functions (Google style)
- No `print()` — use `logging`
- Async all the way — all HTTP calls are `await`-ed
- Line length: 100 (`ruff`)

---

## Pre-commit hooks

`backend/imdbapi/.pre-commit-config.yaml` — install and run from this directory.

```bash
uv run pre-commit install    # once per clone
uv run pre-commit run --all-files
```

| Hook | Notes |
|---|---|
| `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-case-conflict`, `check-merge-conflict` | File health |
| `check-added-large-files`, `check-illegal-windows-names`, `detect-private-key` | Safety |
| `pretty-format-json` | JSON files auto-formatted |
| `sort-simple-yaml` | YAML keys sorted |
| `detect-secrets` | No API keys or tokens |
| `mypy` (strict, extra dep: `pydantic`) | Type checking |
| `ruff-check --fix`, `ruff-format` | Linting and formatting |

**Never `--no-verify`.** False-positive → `# pragma: allowlist secret` + `detect-secrets scan > .secrets.baseline`.

---

## VSCode setup

`backend/imdbapi/.vscode/` is committed with a full workspace configuration:
- `settings.json` — Python interpreter (`backend/.venv` via `../`), Ruff, mypy strict, pytest discovery
- `extensions.json` — Python, debugpy, Ruff, mypy, TOML, GitLens
- `launch.json` — `main.py` interactive runner + pytest all / current file
- `tasks.json` — lint, format, test, test with coverage, pre-commit

**Interpreter:** Run `uv sync --all-packages` from `backend/` — creates `backend/.venv/`

---

## Session start protocol

1. `gh issue list --repo aharbii/movie-finder --state open`
2. Create issue in `aharbii/movie-finder`, then `aharbii/imdbapi-client` linked
3. Create branch + work through checklist

---

## Branching and commits

```
feature/<kebab>  fix/<kebab>  chore/<kebab>  docs/<kebab>
```

Conventional Commits: `fix(imdbapi): reduce retry base delay to 2s`

---

## Cross-cutting change checklist

### 1. GitHub issues
- [ ] `aharbii/movie-finder` (parent)
- [ ] `aharbii/imdbapi-client` linked

### 2. Branch
- [ ] Branch in this repo + `chore/` in `backend/` and root `movie-finder`

### 3. ADR
- [ ] Retry strategy change, new external dependency, or API contract decision?
  → `docs/architecture/decisions/ADR-NNN-title.md`

### 4. Implementation and tests
- [ ] Adapter pattern preserved — no raw HTTP responses exposed
- [ ] Pydantic model updated if `imdbapi.dev` API schema changed
- [ ] `ruff` + `mypy --strict` pass
- [ ] Pre-commit hooks pass
- [ ] `pytest --asyncio-mode=auto` passes

### 5. Environment and secrets
- [ ] `.env.example` updated if any new config added
- [ ] Retry/timeout changes flagged to `chain/` team (SSE timeout budget affected)

### 6. Docker
- [ ] `Dockerfile` updated if new deps
- [ ] `docker-compose.yml` if needed

### 7. CI — Jenkins
- [ ] `Jenkinsfile` reviewed

### 8. Architecture diagrams (in `docs/` submodule)
- [ ] **PlantUML** — `08-seq-chat-sse.puml` or `09-seq-langgraph-execution.puml` if timing or interface changed
  **Never generate `.mdj`**
- [ ] **Structurizr C4** — `workspace.dsl` if external system relation changed

### 9. Documentation
- [ ] `README.md` updated (API coverage table, retry config)
- [ ] `CHANGELOG.md` under `[Unreleased]`

### 10. Sibling submodules affected
| Submodule | Why |
|---|---|
| `backend/chain/` | `enrich_imdb` node consumes this client — response shape changes are breaking |
| `docs/` | Integration and sequence docs |

### 11. Submodule pointer bump
```bash
git add imdbapi && git commit -m "chore(imdbapi): bump to latest main"   # in backend/
git add backend && git commit -m "chore(backend): bump to latest main"   # in root
```

### 12. Pull request
- [ ] PR in `aharbii/imdbapi-client`
- [ ] PR in `aharbii/movie-finder-backend` (pointer bump)
- [ ] PR in `aharbii/movie-finder` (pointer bump)
