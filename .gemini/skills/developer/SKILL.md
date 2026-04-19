---
name: developer
description: Activate when implementing a GitHub issue in the imdbapi-client repo — writing async HTTP client methods, response mapping, retry logic, or domain type adapters.
---

## Role

You are a developer working inside `aharbii/imdbapi-client` — the async IMDb REST client using the Adapter pattern.
Implement the issue fully: code, tests, pre-commit pass. Do not open PRs or push.

## Before writing any code

1. Confirm the issue has an **Agent Briefing** section. If absent, stop and ask for it.
2. Identify whether the change is in: HTTP transport, response parsing, domain mapping, or retry logic.
3. Run `make help` to discover available targets, then `make check` to establish a clean baseline.

## Implementation rules

- **Adapter pattern is mandatory** — the client wraps the external IMDb API and maps responses to internal domain types. Callers never see raw HTTP responses or external API shapes.
- New endpoint = new method on the client class + new domain type if needed. Never expose raw `dict` or `httpx.Response` to callers.
- Async all the way — use `httpx.AsyncClient`; never call blocking HTTP in an async context.
- Retry logic must be carefully bounded — the current 30 s base delay is a known issue; do not increase it further.
- Type annotations required on all public functions; `mypy --strict` must pass.
- No bare `except:` — always catch specific exception types (e.g., `httpx.HTTPStatusError`, `httpx.TimeoutException`).
- Settings via `config.py` / Pydantic `BaseSettings` — no `os.getenv()` scattered in code.

## Quality gate

```bash
make check   # runs ruff + mypy + pytest; discover exact targets with make help
```

## Pointer-bump sequence (THREE levels required)

After your branch is merged in `aharbii/imdbapi-client`:

```bash
# Level 1 — bump imdbapi inside chain/
cd /home/aharbi/workset/movie-finder/backend/chain
git add imdbapi
git commit -m "chore(imdbapi): bump to latest main"

# Level 2 — bump chain inside backend/
cd /home/aharbi/workset/movie-finder/backend
git add chain
git commit -m "chore(chain): bump to latest main"

# Level 3 — bump backend inside root
cd /home/aharbi/workset/movie-finder
git add backend
git commit -m "chore(backend): bump to latest main"
```

## gh commands for this repo

```bash
gh issue list --repo aharbii/imdbapi-client --state open
gh pr create  --repo aharbii/imdbapi-client --base main
```
