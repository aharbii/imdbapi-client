# IMDbAPI Client

A production-ready, fully-typed **async** Python client for the free [imdbapi.dev](https://imdbapi.dev) REST API (v2.7.12).

Contributor workflow in this repo is **strictly Docker-only**: all quality gates (lint,
test, typecheck, test-coverage, pre-commit) execute through the provided `Makefile`.
Host-managed Python environments are not supported for development.

Built with:

- **[httpx](https://www.python-httpx.org/)** — async HTTP with connection pooling
- **[Pydantic v2](https://docs.pydantic.dev/)** — response validation & camelCase → snake_case mapping
- **[tenacity](https://tenacity.readthedocs.io/)** — configurable exponential back-off retries
- **[uv](https://docs.astral.sh/uv/)** — dependency management inside Docker
- **[ruff](https://docs.astral.sh/ruff/)** + **[mypy](https://mypy.readthedocs.io/)** — linting and strict type-checking

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Coverage](#api-coverage)
- [Pagination](#pagination)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Docker](#docker)
- [Package Distribution](#package-distribution)

---

## Features

- **Fully async** — built on `httpx.AsyncClient`; sync usage via `asyncio.run()`
- **All 23 endpoints** — titles, names, interests, search, charts
- **Typed models** — every response is a Pydantic model with absolute import paths
- **Auto-paginator** — `AsyncPaginator` follows `nextPageToken` cursors automatically
- **Retry on transient errors** — 5xx, timeouts, connection failures with exponential back-off
- **Structured exceptions** — `IMDBAPINotFoundError`, `IMDBAPIRateLimitError`, etc.
- **Forward-compatible** — unknown API fields are silently ignored (`extra="ignore"`)
- **Zero secrets** — no API key required; optional `X-API-Key` header support

---

## Project Structure

```text
src/
  imdbapi/
    __init__.py          # Public re-exports: IMDBAPIClient + exceptions
    client.py            # IMDBAPIClient — HTTP layer, retry, error mapping
    exceptions.py        # Exception hierarchy
    pagination.py        # AsyncPaginator generic iterator
    py.typed             # PEP 561 type marker
    utils/
      logger.py          # get_logger() factory (nested under imdbapi)
    models/
      __init__.py        # Flat re-export of all Pydantic models
      common.py          # Shared: Image, Country, Rating, Money, …
      title.py           # Title, Episode, Credit, BoxOffice, …
      name.py            # Name, NameMeterRanking, NameTrivia, …
      interest.py        # Interest, InterestCategory, …
    endpoints/
      __init__.py
      base.py            # BaseEndpoint (_get helper, _clean)
      titles.py          # TitlesEndpoint (18 operations)
      names.py           # NamesEndpoint (7 operations)
      interests.py       # InterestsEndpoint (2 operations)
      search.py          # SearchEndpoint (1 operation)
      charts.py          # ChartsEndpoint (1 operation + paginator)
tests/
  conftest.py            # Shared fixtures + sample payloads
  test_client.py         # HTTP error mapping, retry, lifecycle
  test_titles.py         # All title endpoint tests
  test_names.py          # All name endpoint tests
  test_interests.py      # Interest endpoint tests
  test_search.py         # Search + charts tests
  test_pagination.py     # AsyncPaginator multi-page iteration
Dockerfile               # Multi-stage build (builder + runtime + dev)
docker-compose.yml       # Dev container for Docker-only tasks
Makefile                 # Docker-backed repo targets (DNA aligned with backend)
.env.example             # Standardized environment template
pyproject.toml           # Project metadata and absolute package config
.vscode/                 # Attached-container editor configuration
```

---

## Installation

### For consumers (host environment)

```bash
# Using uv
uv add git+https://github.com/aharbii/imdbapi-client

# Using pip
pip install git+https://github.com/aharbii/imdbapi-client
```

### For contributors (Docker-only)

```bash
make init       # build dev image, create .env from template, install git pre-commit hook
make editor-up  # start container for VS Code attach
```

---

## Quick Start

### Async context-manager (recommended)

```python
import asyncio
from imdbapi import IMDBAPIClient

async def main():
    async with IMDBAPIClient() as client:
        # Full-text search
        results = await client.search.titles("Inception", limit=5)
        for t in results.titles:
            print(t.primary_title, t.start_year)

        # Fetch full title record
        title = await client.titles.get("tt1375666")
        print(title.rating.aggregate_rating if title.rating else "N/A")

        # Fetch a person
        person = await client.names.get("nm0634240")
        print(person.display_name, person.primary_professions)

if __name__ == "__main__":
    asyncio.run(main())
```

### Sync usage

```python
import asyncio
from imdbapi import IMDBAPIClient

client = IMDBAPIClient()
title = asyncio.run(client.titles.get("tt0111161"))
print(title.primary_title)
asyncio.run(client.close())
```

### Integrating into a larger project

Always use absolute imports when integrating the library:

```python
from imdbapi import IMDBAPIClient
from imdbapi.models import TitleType, SortBy

class MovieService:
    def __init__(self):
        self._imdb = IMDBAPIClient(timeout=15.0, max_retries=3)

    async def startup(self):
        await self._imdb.open()

    async def shutdown(self):
        await self._imdb.close()

    async def get_top_drama_movies(self):
        return await self._imdb.titles.list(
            types=[TitleType.MOVIE],
            genres=["Drama"],
            sort_by=SortBy.USER_RATING,
            min_vote_count=10_000,
        )
```

### Logging

Use the provided logger factory in your own modules (always use absolute imports):

```python
from imdbapi.utils.logger import get_logger
logger = get_logger(__name__)

# Enable debug mode on the client for verbose HTTP logs:
client = IMDBAPIClient(debug=True)
```

Logs go to both stdout and timestamped log files under `./logs/`.

---

## API Coverage

### Titles (`client.titles`)

| Method                             | Endpoint                                 |
| ---------------------------------- | ---------------------------------------- |
| `get(title_id)`                    | `GET /titles/{titleId}`                  |
| `list(**filters)`                  | `GET /titles`                            |
| `list_pages(**filters)`            | auto-paginated `GET /titles`             |
| `batch_get(title_ids)`             | `GET /titles:batchGet`                   |
| `get_credits(title_id)`            | `GET /titles/{titleId}/credits`          |
| `get_credits_pages(title_id)`      | auto-paginated credits                   |
| `get_release_dates(title_id)`      | `GET /titles/{titleId}/releaseDates`     |
| `get_akas(title_id)`               | `GET /titles/{titleId}/akas`             |
| `get_seasons(title_id)`            | `GET /titles/{titleId}/seasons`          |
| `get_episodes(title_id, season=…)` | `GET /titles/{titleId}/episodes`         |
| `get_episodes_pages(title_id)`     | auto-paginated episodes                  |
| `get_images(title_id)`             | `GET /titles/{titleId}/images`           |
| `get_videos(title_id)`             | `GET /titles/{titleId}/videos`           |
| `get_award_nominations(title_id)`  | `GET /titles/{titleId}/awardNominations` |
| `get_parents_guide(title_id)`      | `GET /titles/{titleId}/parentsGuide`     |
| `get_certificates(title_id)`       | `GET /titles/{titleId}/certificates`     |
| `get_company_credits(title_id)`    | `GET /titles/{titleId}/companyCredits`   |
| `get_box_office(title_id)`         | `GET /titles/{titleId}/boxOffice`        |

### Names (`client.names`)

| Method                           | Endpoint                            |
| -------------------------------- | ----------------------------------- |
| `get(name_id)`                   | `GET /names/{nameId}`               |
| `batch_get(name_ids)`            | `GET /names:batchGet`               |
| `get_images(name_id)`            | `GET /names/{nameId}/images`        |
| `get_filmography(name_id)`       | `GET /names/{nameId}/filmography`   |
| `get_filmography_pages(name_id)` | auto-paginated filmography          |
| `get_relationships(name_id)`     | `GET /names/{nameId}/relationships` |
| `get_trivia(name_id)`            | `GET /names/{nameId}/trivia`        |

### Interests (`client.interests`)

| Method              | Endpoint                      |
| ------------------- | ----------------------------- |
| `list_categories()` | `GET /interests`              |
| `get(interest_id)`  | `GET /interests/{interestId}` |

### Search (`client.search`)

| Method                   | Endpoint             |
| ------------------------ | -------------------- |
| `titles(query, limit=…)` | `GET /search/titles` |

### Charts (`client.charts`)

| Method                    | Endpoint                 |
| ------------------------- | ------------------------ |
| `starmeter(page_token=…)` | `GET /chart/starmeter`   |
| `starmeter_pages()`       | auto-paginated starmeter |

---

## Pagination

Any endpoint returning `nextPageToken` has a `*_pages()` method that returns
an `AsyncPaginator` — an async iterator that automatically follows cursors:

```python
async with IMDBAPIClient() as client:
    # Collect all action movies across multiple pages
    all_titles = []
    async for page in client.titles.list_pages(genres=["Action"], min_aggregate_rating=7.0):
        all_titles.extend(page.titles)

    # All StarMeter rankings
    async for page in client.charts.starmeter_pages():
        for person in page.names:
            print(person.display_name, person.meter_ranking)

    # All episodes of Breaking Bad
    async for page in client.titles.get_episodes_pages("tt0903747"):
        for ep in page.episodes:
            print(f"S{ep.season}E{ep.episode_number} — {ep.title}")
```

---

## Error Handling

```python
from imdbapi import IMDBAPIClient
from imdbapi.exceptions import (
    IMDBAPINotFoundError,
    IMDBAPIRateLimitError,
    IMDBAPIServerError,
    IMDBAPIConnectionError,
    IMDBAPITimeoutError,
    IMDBAPIValidationError,
)

async with IMDBAPIClient() as client:
    try:
        title = await client.titles.get("tt9999999")
    except IMDBAPINotFoundError:
        print("Title not found")
    except IMDBAPIRateLimitError:
        print("Rate limit — back off and retry")
    except IMDBAPIServerError as exc:
        print(f"Server error {exc.status_code}: {exc.message}")
    except IMDBAPIConnectionError:
        print("Network unreachable")
    except IMDBAPITimeoutError:
        print("Request timed out")
    except IMDBAPIValidationError as exc:
        print(f"Unexpected response shape: {exc}")
```

### Exception hierarchy

```
IMDBAPIError
├── IMDBAPIHTTPError          (has .status_code, .message, .details)
│   ├── IMDBAPIBadRequestError    # 400 — invalid params
│   ├── IMDBAPINotFoundError      # 404 — resource missing
│   ├── IMDBAPIRateLimitError     # 429 — too many requests
│   └── IMDBAPIServerError        # 5xx — retried automatically
├── IMDBAPIConnectionError        # DNS / connect failure (retried)
├── IMDBAPITimeoutError           # Request timeout (retried)
└── IMDBAPIValidationError        # Response schema mismatch
```

Retryable errors are retried with exponential back-off (1s → 2s → 4s …, max 10s)
before being raised to the caller.

---

## Configuration

```python
client = IMDBAPIClient(
    base_url="https://api.imdbapi.dev",   # override for local mock servers
    timeout=30.0,                          # total request timeout in seconds
    max_retries=3,                         # set to 1 to disable retries
    api_key="your-key-if-needed",          # optional X-API-Key header  # pragma: allowlist secret
    debug=True,                            # DEBUG-level request/response logs
)
```

---

## Development

Contributor setup is **strictly Docker-only**. You do not need a host-managed
Python interpreter or `uv` installation to develop on this project.

### Prerequisites

- Docker 24+ with the Compose plugin
- `make`

### Common commands

```bash
make init           # build dev image, create .env from template, install git hook
make editor-up      # start container for VS Code attach
make shell          # open bash shell in the container
make lint           # ruff check (report only)
make fix            # ruff check --fix + ruff format (auto-apply)
make format         # ruff format
make typecheck      # mypy --strict (covers src + tests)
make test           # pytest
make test-coverage  # pytest + coverage XML/HTML + JUnit report
make detect-secrets # standalone secret scan
make pre-commit     # full hook suite (also enforced on git commit)
make check          # lint + typecheck + test-coverage (CI gate)
make ci-down        # full cleanup (volumes + images)
```

### VS Code

1. Run `make editor-up`.
2. Use `Dev Containers: Attach to Running Container...`.
3. Attach to the `imdbapi` container started from this repo.
4. Use the committed tasks and launch configurations from that attached session.

---

## Testing

All tests use `respx` to mock HTTP — **no real network traffic**:

```bash
make test
make test-coverage
```

To run a specific test from within the container:

```bash
pytest tests/test_titles.py -v -k "test_get"
```

---

## Docker

This repository uses a multi-stage `Dockerfile` to ensure environment parity
across development and production.

| Stage     | Purpose                                      |
| --------- | -------------------------------------------- |
| `dev`     | Local development (includes lint/test tools) |
| `builder` | Dependency synchronization                   |
| `runtime` | Lean production image                        |

---

## Package Distribution

Packaging and image publication are handled in CI from the `runtime` stage
defined in [Dockerfile](Dockerfile).

### Install in another project

```toml
# pyproject.toml
[project]
dependencies = ["imdbapi-client>=0.1.0"]
```

---

## License

MIT
