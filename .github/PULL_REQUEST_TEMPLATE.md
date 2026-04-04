## What and why

<!-- What changed and why? Link the issue this addresses. -->

Closes #

## Type of change

- [ ] New or updated endpoint
- [ ] Retry / resilience configuration change
- [ ] Pydantic model update (imdbapi.dev schema change)
- [ ] Bug fix
- [ ] Chore (tooling, dependencies, CI config)
- [ ] Documentation only

## How to test

1.
2.
3.

## CI status

The following Jenkins stages must be green before merge:

| Stage      | Command              | Trigger |
| ---------- | -------------------- | ------- |
| Lint       | `make lint`          | All PRs |
| Type-check | `make typecheck`     | All PRs |
| Test       | `make test-coverage` | All PRs |

## Checklist

### Code quality

- [ ] `make lint` passes — zero errors (`ruff`, line length 100)
- [ ] `make typecheck` passes — `mypy --strict` zero errors
- [ ] `make test` passes — zero failures (all tests use `respx` HTTP mocking — no real network calls)
- [ ] New endpoints have tests covering: success, 404, 429, 5xx (retried), and connection-error paths
- [ ] No bare `except:` — catches `httpx.HTTPStatusError`, `httpx.RequestError`, `tenacity.RetryError`

### Documentation

- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] `README.md` API coverage table updated if endpoints were added or removed

### Cross-repo impact _(if applicable)_

- [ ] Retry or timeout change — coordinated with `chain/` team (change may affect SSE streaming budget)
- [ ] Response model field added or renamed — verify `chain/nodes/imdb_enrichment.py` still compiles

### Review

- [ ] PR title follows `type(scope): summary` (≤72 chars, imperative mood, lowercase)
- [ ] PR description links the issue and discloses the AI authoring tool + model used
- [ ] Any AI-assisted review comment or approval discloses the review tool + model

### Release _(for release PRs only)_

- [ ] `version` bumped in `pyproject.toml`
- [ ] `[Unreleased]` section moved to the new version in `CHANGELOG.md`
- [ ] Git tag created after merge: `git tag vX.Y.Z && git push origin --tags`
- [ ] Backend pointer-bump PR opened in `aharbii/movie-finder-backend`
