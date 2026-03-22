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

The imdbapi-client is a **standalone repo** with its own `uv.lock`. It can also run as a workspace member of the backend repo.

### Standalone

```bash
cd imdbapi/
uv sync --group dev
cp .env.example .env && $EDITOR .env
uv run pre-commit install
```

### As a workspace member (from backend root)

```bash
cd backend/
uv sync --group dev
# imdbapi is installed as an editable workspace member
```

### Minimum required environment variables

```
IMDB_API_KEY=    # required for all endpoint calls
IMDB_BASE_URL=   # the API base URL
```

---

## Project structure

```
imdbapi/
├── src/
│   ├── imdbapi/
│   │   ├── __init__.py          ← public re-exports (IMDBAPIClient, models, exceptions)
│   │   ├── client.py            ← IMDBAPIClient — main entry point
│   │   ├── exceptions.py        ← exception hierarchy
│   │   ├── pagination.py        ← AsyncPaginator generic iterator
│   │   ├── py.typed             ← PEP 561 marker (typed package)
│   │   ├── endpoints/
│   │   │   ├── base.py          ← BaseEndpoint (shared HTTP helpers)
│   │   │   ├── titles.py        ← 18 title operations
│   │   │   ├── names.py         ← 7 name operations
│   │   │   ├── interests.py     ← 2 interest operations
│   │   │   ├── search.py        ← 1 search operation
│   │   │   └── charts.py        ← starmeter + paginator
│   │   ├── langchain/
│   │   │   ├── agent.py         ← create_movie_agent() factory
│   │   │   └── tools.py         ← create_imdb_tools() → ReAct tool list
│   │   └── models/
│   │       ├── common.py        ← shared types: Image, Rating, Country, Money
│   │       ├── title.py         ← Title, Episode, Credit, BoxOffice, etc.
│   │       ├── name.py          ← Name, NameMeterRanking, NameTrivia
│   │       └── interest.py      ← Interest, InterestCategory
│   └── utils/
│       └── logger.py            ← get_logger factory
├── tests/
│   ├── conftest.py              ← shared fixtures (mock client, base URL)
│   ├── test_client.py           ← HTTP error mapping, retry, lifecycle
│   ├── test_titles.py
│   ├── test_names.py
│   ├── test_interests.py
│   ├── test_search.py
│   └── test_pagination.py
├── examples/
│   └── langchain_agent_example.py  ← 5 demos: one-shot, multi-turn, streaming, etc.
└── main.py                      ← quick smoke-test / demo runner
```

---

## Adding a new endpoint

All endpoints follow the same pattern. Here's how to add a new one:

### 1. Add the model (if needed) in `src/imdbapi/models/`

```python
# src/imdbapi/models/title.py  (or a new file)
from pydantic import BaseModel, Field

class MyNewResource(BaseModel):
    id: str
    name: str
    some_field: str | None = Field(default=None)
```

Export it from `src/imdbapi/models/__init__.py`.

### 2. Add the method to the appropriate endpoint class

```python
# src/imdbapi/endpoints/titles.py
async def get_my_resource(self, title_id: str) -> MyNewResource:
    """Fetch my new resource for a title.

    Args:
        title_id: The IMDb title ID (e.g. "tt1234567").

    Returns:
        MyNewResource with the fetched data.

    Raises:
        IMDBAPIHTTPError: On 4xx/5xx responses.
        IMDBAPIConnectionError: On network failure.
    """
    data = await self._get(f"/titles/{title_id}/my-resource")
    return MyNewResource.model_validate(data)
```

### 3. Export from `src/imdbapi/__init__.py`

```python
from imdbapi.models import MyNewResource
__all__ = [..., "MyNewResource"]
```

### 4. Add a LangChain tool if useful for agent integration

```python
# src/imdbapi/langchain/tools.py
@tool
async def get_my_resource(title_id: str) -> str:
    """Get my new resource. Use when ..."""
    async with IMDBAPIClient(...) as client:
        result = await client.titles.get_my_resource(title_id)
        return result.model_dump_json()
```

---

## Working with models

All models use **Pydantic v2**. Key conventions:

- Optional fields default to `None`: `field: str | None = None`
- Use `Field(alias="camelCase")` when the API returns camelCase keys
- Nested models are validated recursively — no manual parsing
- Use `model_validate(data)` not `MyModel(**data)` for dict input

---

## Pagination

The `AsyncPaginator` in `pagination.py` is a generic async iterator for any list endpoint:

```python
# Usage (already handled in endpoint methods like list_pages, starmeter_pages)
paginator = AsyncPaginator(fetch_fn=client.titles.list, page_size=50)
async for page in paginator:
    for title in page:
        process(title)
```

When adding a new paginated endpoint, follow the `charts.starmeter_pages()` pattern.

---

## Error handling

The exception hierarchy (`exceptions.py`):

```
IMDBAPIError (base)
├── IMDBAPIHTTPError     ← 4xx / 5xx responses (has .status_code)
├── IMDBAPIConnectionError ← network failure / DNS
├── IMDBAPITimeoutError  ← request timeout
└── IMDBAPIValidationError ← Pydantic validation failure
```

The client retries automatically on `5xx`, `IMDBAPITimeoutError`, and `IMDBAPIConnectionError` with exponential backoff (configured via `max_retries`). Do not add manual retry logic in calling code.

---

## Testing strategy

**Rule: no real HTTP calls.** All tests use [respx](https://lundberg.github.io/respx/) to mock `httpx` at the transport level.

### Basic test pattern

```python
import respx
import httpx
import pytest
from imdbapi import IMDBAPIClient

BASE_URL = "https://api.example.com"

@pytest.fixture
def client():
    return IMDBAPIClient(base_url=BASE_URL, api_key="test-key")

@respx.mock
async def test_get_title(client):
    respx.get(f"{BASE_URL}/titles/tt1234567").mock(
        return_value=httpx.Response(200, json={"id": "tt1234567", "titleText": {"text": "Test"}})
    )
    async with client:
        title = await client.titles.get("tt1234567")
    assert title.id == "tt1234567"
```

### Testing error handling

```python
@respx.mock
async def test_404_raises(client):
    respx.get(f"{BASE_URL}/titles/tt9999999").mock(
        return_value=httpx.Response(404, json={"error": "not found"})
    )
    with pytest.raises(IMDBAPIHTTPError) as exc_info:
        async with client:
            await client.titles.get("tt9999999")
    assert exc_info.value.status_code == 404
```

### Running tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run pytest tests/test_titles.py -v -k "test_get"
```

---

## LangChain integration

The `src/imdbapi/langchain/` module is **optional** — only installed with the `agents-anthropic` or `agents-openai` dependency groups:

```bash
uv sync --group agents-anthropic   # Claude backend
uv sync --group agents-openai      # GPT backend
```

When adding a new tool, follow the pattern in `tools.py`:
- Use `@tool` decorator from `langchain_core.tools`
- Keep the docstring clear — it becomes the tool description the LLM sees
- Return a string (JSON-encoded model output works well)
- Handle `IMDBAPIError` gracefully and return a human-readable error message
