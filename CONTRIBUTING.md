# Contributing to imdbapi-client

The imdbapi-client is a **fully typed async Python client** for the IMDb REST API. It is used by the `chain` package and can also be used standalone with LangChain agent integrations.

For org-wide conventions (branching, commits, PRs, release process) see the [backend CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Table of contents

1. [Development setup](#development-setup)
2. [Project structure](#project-structure)
3. [Adding a new endpoint](#adding-a-new-endpoint)
4. [Working with models](#working-with-models)
5. [Pagination](#pagination)
6. [Error handling](#error-handling)
7. [Testing strategy](#testing-strategy)
8. [LangChain integration](#langchain-integration)

---

## Development setup

The supported contributor workflow is **strictly Docker-only**. All development
tasks, including linting, testing, and type-checking, execute inside the
provided container environment via the `Makefile`.

### Repo-local setup

```bash
cd imdbapi/
cp .env.example .env
make init           # build the dev image
make editor-up      # start the long-lived dev container
```

### Common commands

```bash
make lint           # ruff check
make format         # ruff format
make typecheck      # mypy strict (covers src + tests)
make test           # pytest
make test-coverage  # pytest + coverage report
make detect-secrets # standalone secret scan
make pre-commit     # mirrored repo hooks
make check          # lint + typecheck + test
make ci-down        # full cleanup (volumes + images)
```

### VS Code

1. Run `make editor-up`.
2. In VS Code, use `Dev Containers: Attach to Running Container...`.
3. Select the `imdbapi` container started from this repo.
4. Use the committed tasks and launch configurations from that attached session.
5. Stop the container with `make editor-down` when done.

### Required environment variables

The core client requires **no mandatory environment variables**. See
`.env.example` for optional observability and AI agent keys.

---

## Project structure

```text
imdbapi/
├── src/
│   ├── imdbapi/
│   │   ├── __init__.py          # public re-exports
│   │   ├── client.py            # IMDBAPIClient entry point
│   │   ├── exceptions.py        # exception hierarchy
│   │   ├── pagination.py        # AsyncPaginator
│   │   ├── py.typed             # PEP 561 marker
│   │   ├── endpoints/           # concrete resource groups
│   │   ├── langchain/           # LangChain agent + tools
│   │   ├── models/              # Pydantic models
│   │   └── utils/               # absolute namespace utilities
│   │       └── logger.py
├── tests/
│   ├── conftest.py              # shared fixtures
│   ├── test_client.py
│   └── ...
├── examples/
│   └── langchain_agent_example.py
└── main.py                      # smoke-test runner
```

---

## Adding a new endpoint

### 1. Add the model

Define the model in `src/imdbapi/models/` using Pydantic v2. Always use
absolute imports for shared common types.

```python
from pydantic import BaseModel
from imdbapi.models.common import Image
```

### 2. Add the method

Add the method to the appropriate endpoint class in `src/imdbapi/endpoints/`.
Use the `_get` helper and ensure the response is validated via the model.

```python
async def get_something(self, id: str) -> MyModel:
    data = await self._get(f"/something/{id}")
    return MyModel.model_validate(data)
```

### 3. Absolute Imports Mandate

**Never use relative imports.** Every internal import must use the absolute
`imdbapi.*` namespace to ensure the package remains independently usable.

Correct:
```python
from imdbapi.utils.logger import get_logger
```

Incorrect:
```python
from ..utils.logger import get_logger
```

---

## Working with models

- Optional fields default to `None`: `field: str | None = None`
- Use `Field(alias="camelCase")` for API parity
- Use `model_validate(data)` for validation

---

## Pagination

Use `AsyncPaginator` for any endpoint returning `nextPageToken`. Follow the
existing pattern in `ChartsEndpoint.starmeter_pages()`.

---

## Error handling

The client retries automatically on transient errors (5xx, timeouts, connection
failures) with exponential backoff. Do not implement manual retry logic in
endpoint methods.

---

## Testing strategy

**Rule: no real HTTP calls.** Use `respx` to mock transport-level responses.

```bash
make test
make test-coverage
```

To run a specific test from within the container:
```bash
pytest tests/test_titles.py -v -k "test_get"
```

---

## LangChain integration

The `src/imdbapi/langchain/` module is optional. To develop on it, install the
extra groups **inside the container**:

```bash
# Inside make shell
uv sync --frozen --group agents-anthropic --active
```
