"""Tests for the InterestsEndpoint."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from imdbapi.client import IMDBAPIClient
from imdbapi.exceptions import IMDBAPINotFoundError
from imdbapi.models import Interest, ListInterestCategoriesResponse

BASE_URL = "https://api.imdbapi.dev"


@pytest.fixture
def client() -> IMDBAPIClient:
    return IMDBAPIClient(base_url=BASE_URL, max_retries=1)


# ---------------------------------------------------------------------------
# list_categories()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_interest_categories(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "categories": [
            {
                "category": "Genre",
                "interests": [
                    {"id": "ge0000007", "name": "Drama"},
                    {"id": "ge0000001", "name": "Crime"},
                ],
            }
        ]
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/interests").mock(return_value=httpx.Response(200, json=payload))
        result = await client.interests.list_categories()
    assert isinstance(result, ListInterestCategoriesResponse)
    assert len(result.categories) == 1
    assert result.categories[0].category == "Genre"
    assert result.categories[0].interests[0].name == "Drama"


@pytest.mark.asyncio
async def test_list_interest_categories_empty(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/interests").mock(
            return_value=httpx.Response(200, json={"categories": []})
        )
        result = await client.interests.list_categories()
    assert result.categories == []


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_interest(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "id": "ge0000007",
        "name": "Drama",
        "description": "Serious, plot-driven presentations.",
        "isSubgenre": False,
        "similarInterests": [{"id": "ge0000001", "name": "Crime"}],
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/interests/ge0000007").mock(return_value=httpx.Response(200, json=payload))
        result = await client.interests.get("ge0000007")
    assert isinstance(result, Interest)
    assert result.id == "ge0000007"
    assert result.name == "Drama"
    assert result.is_subgenre is False
    assert len(result.similar_interests) == 1
    assert result.similar_interests[0].name == "Crime"


@pytest.mark.asyncio
async def test_get_interest_not_found(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/interests/invalid").mock(
            return_value=httpx.Response(404, json={"message": "not found"})
        )
        with pytest.raises(IMDBAPINotFoundError):
            await client.interests.get("invalid")
