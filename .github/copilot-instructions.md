# GitHub Copilot — imdbapi-client

Async IMDb REST client — wraps imdbapi.dev, handles retries, and maps raw responses to internal domain types.

> For full project context, persona prompts, and architecture reference: see root `.github/copilot-instructions.md`.

---

## Python standards

- Pydantic v2 models validate every field — no raw `dict` returned to callers
- Catch specific exceptions: `httpx.HTTPStatusError`, `httpx.RequestError`, `tenacity.RetryError`
- Async all the way — all HTTP calls are `await`-ed
- Tests: `pytest` with `respx` for HTTP-level mocking. No real IMDb API calls in tests.
- Run `make help` for all available targets

---

## Design patterns

| Pattern                  | Rule                                                                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Adapter**              | The client wraps imdbapi.dev and maps to internal domain types. Callers (chain nodes) never see raw HTTP responses or camelCase fields.                 |
| **Resilience decorator** | Retry policy (`tenacity`) is applied at the transport layer only, not inside business logic. New endpoints inherit the policy automatically.            |
| **Configuration object** | Retry settings, timeouts, and base URL are loaded from `config.py` via Pydantic `BaseSettings` — not hardcoded anywhere.                               |

**Retry constraint:** The 30-second retry base delay blocks the SSE stream. Any retry policy change must be coordinated with the `chain/` team to verify the SSE timeout budget.

---

## Key files

| Path          | Description                                                              |
| ------------- | ------------------------------------------------------------------------ |
| `src/`        | Client implementation — adapter, retry logic, Pydantic response models   |
| `config.py`   | All timeout, retry, and base URL settings via Pydantic `BaseSettings`    |
| `pyproject.toml` | Standalone `uv` project with its own `uv.lock`                        |
| `Makefile`    | Docker-only dev contract — run `make help` for all targets               |
