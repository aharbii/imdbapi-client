# Claude Code — imdbapi submodule

This is **`imdbapi-client`** (`backend/chain/imdbapi/`) — part of the Movie Finder project.
GitHub repo: `aharbii/imdbapi-client` · Parent repo: `aharbii/movie-finder`

> See root `CLAUDE.md` for: full submodule map, GitHub issue/PR hygiene, cross-cutting checklist, coding standards, branching strategy, session start protocol.

---

## What this submodule does

Production-ready async Python client for the [imdbapi.dev](https://imdbapi.dev) REST API.
Used by the LangGraph `enrich_imdb` node to enrich movie candidates with live IMDb metadata.

- **HTTP:** `httpx` (async, connection pooling)
- **Validation:** Pydantic v2 (response parsing, camelCase → snake_case mapping)
- **Resilience:** `tenacity` exponential back-off retries (base delay currently 30 s — issue #8)
- **Auth:** imdbapi.dev requires no authentication key
- **Local dev:** Docker-only via `make` + `docker compose`
- **Lifecycle:** Standalone `uv` project with its own `uv.lock`

---

## Technology stack (imdbapi-specific)

| Layer      | Stack                                              |
| ---------- | -------------------------------------------------- |
| Language   | Python 3.13, standalone `uv` project               |
| HTTP       | `httpx` (async)                                    |
| Retry      | `tenacity` (exponential back-off)                  |
| Validation | Pydantic v2                                        |
| Tests      | `pytest --asyncio-mode=auto`                       |
| CI         | Jenkins Multibranch                                |

---

## Environment variables

`imdbapi.dev` requires no API key. Optional (for examples only):

```
OPENAI_API_KEY, ANTHROPIC_API_KEY   # used only in examples/langchain_agent_example.py
```

---

## Design patterns (imdbapi-specific)

| Pattern                  | Where                                 | Rule                                                                                                                                               |
| ------------------------ | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Adapter**              | The entire client                     | Wraps `imdbapi.dev` REST responses and maps them to internal domain types. Callers (chain nodes) never see raw HTTP responses or camelCase fields. |
| **Configuration object** | `config.py` / Pydantic `BaseSettings` | Retry settings, timeouts, base URL loaded from config — not hardcoded.                                                                             |
| **Resilience decorator** | `tenacity` retry logic                | Retry policy is applied at the transport layer, not inside business logic. New endpoints inherit the policy automatically.                         |

**Known issue #8:** The 30-second retry base delay blocks the SSE stream. Any retry policy
change must be coordinated with the `chain/` team to verify the SSE timeout budget.

---

## Coding standards (additions to root CLAUDE.md)

- Pydantic models validate every field — no raw `dict` returned to callers
- Catch specific exceptions: `httpx.HTTPStatusError`, `httpx.RequestError`, `tenacity.RetryError`
- Async all the way — all HTTP calls are `await`-ed

---

## Pre-commit hooks

```bash
make pre-commit
```

Hooks: whitespace/YAML/safety checks, `detect-secrets`, `mypy --strict`, `ruff-check --fix`, `ruff-format`. **Never `--no-verify`.**
False positive → `# pragma: allowlist secret` + `detect-secrets scan > .secrets.baseline`.

---

## VSCode setup

- `settings.json` — attached-container interpreter (`/opt/venv/bin/python`), Ruff, mypy strict, pytest discovery
- `launch.json` — `main.py` interactive runner + pytest all / current file from the container
- `tasks.json` — host-side `make ...` wrappers for build, editor attach, lint, format, test, coverage, pre-commit

**Workflow:** `make editor-up`, then attach via `Dev Containers: Attach to Running Container...`

---

## Workflow invariants (imdbapi-specific)

- Gitlink path is `imdbapi` inside `aharbii/movie-finder-backend`. Parent path filters must use `imdbapi`, not `imdbapi/**`.
- Retry or timeout changes must be flagged to `chain/` — they affect the SSE stream budget.

Run `/session-start` in root workspace.

---

## Branching and commits

```
feature/<kebab>  fix/<kebab>  chore/<kebab>  docs/<kebab>
```

Conventional Commits: `fix(imdbapi): reduce retry base delay to 2s`

---

## Cross-cutting change checklist (imdbapi-specific rows)

| #   | Category           | Key gate                                                                                                                                               |
| --- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **Branch**         | `feature/fix/chore/docs` in this repo + pointer-bump `chore/` in `backend/` and root                                                                   |
| 2   | **ADR**            | Retry strategy change, new external dep, or API contract decision → ADR in `docs/`                                                                     |
| 3   | **Implementation** | Adapter pattern — no raw HTTP responses exposed; Pydantic models updated if `imdbapi.dev` schema changed                                               |
| 4   | **Env & secrets**  | `.env.example` updated if new config; retry/timeout changes flagged to `chain/` (SSE budget)                                                           |
| 5   | **Diagrams**       | `08-seq-chat-sse.puml` or `09-seq-langgraph-execution.puml` if timing/interface changed; `workspace.dsl` if C4 changed; **never `.mdj`**               |

### Sibling submodules affected

| Submodule        | Why                                                                           |
| ---------------- | ----------------------------------------------------------------------------- |
| `backend/chain/` | `enrich_imdb` node consumes this client — response shape changes are breaking |
| `docs/`          | Integration and sequence docs                                                 |

### Submodule pointer bump

```bash
git add imdbapi && git commit -m "chore(imdbapi): bump to latest main"   # in backend/
git add backend && git commit -m "chore(backend): bump to latest main"   # in root
```

### Pull request

- [ ] PR in `aharbii/imdbapi-client` discloses the AI authoring tool + model
- [ ] PR in `aharbii/movie-finder-backend` (pointer bump)
- [ ] PR in `aharbii/movie-finder` (pointer bump)
- [ ] Any AI-assisted review comment or approval discloses the review tool + model
