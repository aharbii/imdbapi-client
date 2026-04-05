# Changelog — imdbapi-client

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- Docker-backed repo-local development contract via `Makefile` and `docker-compose.yml`
- "Editor" lifecycle targets: `make editor-up`, `make editor-down` for isolated dev environment
- Standardized `Makefile` targets: `init`, `up`, `down`, `logs`, `detect-secrets`
- Compatibility aliases: `build`, `run`, `run-dev`, `setup`
- Absolute import mandate for package-like handling and standalone distribution
- Standalone `make detect-secrets` target for container-backed security scanning
- Multi-stage `Dockerfile` with optimized dependency caching (`--no-install-project`)
- `make ci-down` for zero-footprint resource cleanup in CI environments

### Changed

- Removed stale `uv sync --group agents-anthropic` install hint from the `langchain`
  import error message in the movie agent factory
- **Package Restructuring:** Moved `src/utils` to `src/imdbapi/utils` to resolve global namespace pollution
- **Import Refactoring:** Converted all internal relative imports to absolute `imdbapi.*` paths
- **Quality Gate Expansion:** `make typecheck` now enforces strict typing across both `src/` and `tests/`
- **Pre-commit Synchronization:** Reverted to remote mirrors strategy to align with trusted `backend` DNA
- **Naming Parity:** Renamed `make coverage` to `make test-coverage` for cross-repo consistency
- **CI Hygiene:** Updated `Jenkinsfile` to use `make ci-down` for full volume and image cleanup;
  removed Build App Image stage (image builds now orchestrated by the root pipeline)
- All test outputs (`junit.xml`, `coverage.xml`, `htmlcov/`) now written to a `reports/`
  subdirectory; `Makefile` paths updated accordingly; `.gitignore` updated to a single
  `reports/` entry
- GitHub Actions CI workflow updated: added `EnricoMi/publish-unit-test-result-action@v2`,
  `irongut/CodeCoverageSummary@v1.3.0`, and `marocchino/sticky-pull-request-comment@v2`
  reporting plugins mirroring Jenkins plugin behaviour

### Removed

- Host-managed `uv` and Python environment recommendations for contributors

---

## [0.1.0] — 2026-03-22

### Added

- `IMDBAPIClient` — fully async context manager with `httpx` transport
- Automatic retry with exponential backoff via `tenacity` (5xx, timeout, connection errors)
- **Titles** endpoint group (18 operations): `get`, `list`, `list_pages`, `batch_get`, etc.
- Full Pydantic v2 model layer with camelCase to snake_case mapping
- `AsyncPaginator` — generic async iterator for list endpoints
- PEP 561 `py.typed` marker
- Full test suite using `respx` HTTP mocks
