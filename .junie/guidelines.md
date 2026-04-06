# JetBrains AI (Junie) — imdbapi submodule guidelines

This is **`imdbapi-client`** (`backend/chain/imdbapi/`) — Async IMDb REST client.
GitHub repo: `aharbii/imdbapi-client` · Parent: `aharbii/movie-finder`

---

## What this submodule does

Thin async HTTP client wrapping the public IMDb API. Used by `chain/` as a path dependency.

- **Pattern:** Adapter — wraps raw HTTP responses, maps to internal domain types
- **Callers never see raw HTTP** — all responses mapped to typed domain objects
- **Retry logic:** exponential backoff for rate-limited requests
- **uv:** standalone, imported by `backend/chain/` via path dependency

### Key layout

```
src/imdbapi/
├── client.py    Async HTTP client (httpx)
├── models.py    Domain types returned to callers
└── config.py    Settings (base URL, timeout, retry config)
```

---

## Quality commands (Docker-only)

```bash
make pre-commit   # lint + typecheck + format
make test         # pytest --asyncio-mode=auto
make lint         # ruff check
make typecheck    # mypy --strict
```

---

## Design pattern

**Adapter:** the client converts external API responses into internal domain types.
Callers in `chain/nodes/enrich_imdb.py` receive typed domain objects, never raw dicts.
Any API contract change must be absorbed here — not propagated to callers.

---

## Python standards

- `mypy --strict` must pass
- No bare `except:` — catch `httpx.HTTPError`, `httpx.TimeoutException` specifically
- Docstrings (Google style) on all public functions and classes
- Async all the way — never call blocking I/O in async context
- Line length: 100

---

## Workflow

- Branches: `feature/<kebab>`, `fix/<kebab>`, `chore/<kebab>`
- Commits: `fix(imdbapi): increase retry backoff for Cloudflare rate limits`
- Pre-commit: `make pre-commit` (Docker)
- After merge: bump pointer in `chain/`, then `backend/`, then root `movie-finder`

---

## Submodule pointer bump

```bash
git add imdbapi && git commit -m "chore(imdbapi): bump to latest main"  # in chain/
git add chain && git commit -m "chore(chain): bump to latest main"       # in backend/
git add backend && git commit -m "chore(backend): bump to latest main"   # in root
```
