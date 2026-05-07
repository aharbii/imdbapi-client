"""Tests for the SearchEndpoint and ChartsEndpoint."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from imdbapi.client import IMDBAPIClient
from imdbapi.exceptions import IMDBAPIValidationError
from imdbapi.models import ListStarMetersResponse, SearchTitlesResponse

BASE_URL = "https://api.imdbapi.dev"


@pytest.fixture
def client() -> IMDBAPIClient:
    return IMDBAPIClient(base_url=BASE_URL, max_retries=1)


@pytest.fixture
def title_payload() -> dict[str, Any]:
    return {
        "id": "tt0111161",
        "type": "MOVIE",
        "isAdult": False,
        "primaryTitle": "The Shawshank Redemption",
        "startYear": 1994,
        "genres": ["Drama"],
        "rating": {"aggregateRating": 9.3, "voteCount": 2_800_000},
        "directors": [],
        "stars": [],
        "writers": [],
        "originCountries": [],
        "spokenLanguages": [],
        "interests": [],
    }


# ---------------------------------------------------------------------------
# search.titles()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_titles(client: IMDBAPIClient, title_payload: dict[str, Any]) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/search/titles").mock(
            return_value=httpx.Response(200, json={"titles": [title_payload]})
        )
        result = await client.search.titles("Shawshank")
    assert isinstance(result, SearchTitlesResponse)
    assert len(result.titles) == 1
    assert result.titles[0].primary_title == "The Shawshank Redemption"


@pytest.mark.asyncio
async def test_search_titles_empty(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/search/titles").mock(return_value=httpx.Response(200, json={"titles": []}))
        result = await client.search.titles("xyznonexistent")
    assert result.titles == []


@pytest.mark.asyncio
async def test_search_titles_with_limit(
    client: IMDBAPIClient, title_payload: dict[str, Any]
) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        route = mock.get("/search/titles").mock(
            return_value=httpx.Response(200, json={"titles": [title_payload]})
        )
        result = await client.search.titles("drama", limit=5)
    assert isinstance(result, SearchTitlesResponse)
    assert route.called


# ---------------------------------------------------------------------------
# charts.starmeter()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_starmeter(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "names": [
            {
                "id": "nm0001104",
                "displayName": "Frank Darabont",
                "meterRanking": {"currentRank": 1, "changeDirection": "UP", "difference": 2},
            }
        ],
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/chart/starmeter").mock(return_value=httpx.Response(200, json=payload))
        result = await client.charts.starmeter()
    assert isinstance(result, ListStarMetersResponse)
    assert result.names[0].display_name == "Frank Darabont"
    assert result.names[0].meter_ranking is not None
    assert result.names[0].meter_ranking.current_rank == 1


@pytest.mark.asyncio
async def test_starmeter_with_page_token(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "names": [],
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        route = mock.get("/chart/starmeter").mock(return_value=httpx.Response(200, json=payload))
        result = await client.charts.starmeter(page_token="cursor_xyz")
    assert isinstance(result, ListStarMetersResponse)
    assert route.called


@pytest.mark.asyncio
async def test_search_titles_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/search/titles?query=test").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.search.titles("test")
