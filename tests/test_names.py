"""Tests for the NamesEndpoint covering all name operations."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from imdbapi.client import IMDBAPIClient
from imdbapi.exceptions import IMDBAPINotFoundError
from imdbapi.models import (
    BatchGetNamesResponse,
    ListNameFilmographyResponse,
    ListNameImagesResponse,
    ListNameRelationshipsResponse,
    ListNameTriviaResponse,
    Name,
)

BASE_URL = "https://api.imdbapi.dev"
NAME_ID = "nm0001104"


@pytest.fixture
def client() -> IMDBAPIClient:
    return IMDBAPIClient(base_url=BASE_URL, max_retries=1)


@pytest.fixture
def name_payload() -> dict[str, Any]:
    return {
        "id": NAME_ID,
        "displayName": "Frank Darabont",
        "alternativeNames": [],
        "primaryImage": {"url": "https://example.com/fd.jpg", "width": 400, "height": 600},
        "primaryProfessions": ["director", "writer"],
        "biography": "Frank Darabont is an American filmmaker born in France.",
        "heightCm": 188,
        "birthName": "Frank Árpád Darabont",
        "birthDate": {"year": 1959, "month": 1, "day": 28},
        "birthLocation": "Montbéliard, France",
        "meterRanking": {"currentRank": 42, "changeDirection": "UP", "difference": 5},
    }


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_name(client: IMDBAPIClient, name_payload: dict[str, Any]) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/names/{NAME_ID}").mock(
            return_value=httpx.Response(200, json=name_payload)
        )
        person = await client.names.get(NAME_ID)
    assert isinstance(person, Name)
    assert person.id == NAME_ID
    assert person.display_name == "Frank Darabont"
    assert "director" in person.primary_professions
    assert person.birth_date is not None
    assert person.birth_date.year == 1959
    assert person.meter_ranking is not None
    assert person.meter_ranking.current_rank == 42
    assert person.meter_ranking.change_direction == "UP"


@pytest.mark.asyncio
async def test_get_name_not_found(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/names/nm9999999").mock(
            return_value=httpx.Response(404, json={"message": "not found"})
        )
        with pytest.raises(IMDBAPINotFoundError):
            await client.names.get("nm9999999")


# ---------------------------------------------------------------------------
# batch_get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_get_names(client: IMDBAPIClient, name_payload: dict[str, Any]) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/names:batchGet").mock(
            return_value=httpx.Response(200, json={"names": [name_payload]})
        )
        result = await client.names.batch_get([NAME_ID])
    assert isinstance(result, BatchGetNamesResponse)
    assert len(result.names) == 1
    assert result.names[0].display_name == "Frank Darabont"


# ---------------------------------------------------------------------------
# get_images()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_name_images(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "images": [{"url": "https://example.com/img.jpg", "width": 400, "height": 600}],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/names/{NAME_ID}/images").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.names.get_images(NAME_ID)
    assert isinstance(result, ListNameImagesResponse)
    assert result.total_count == 1
    assert result.images[0].url == "https://example.com/img.jpg"


# ---------------------------------------------------------------------------
# get_filmography()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_filmography(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "credits": [
            {
                "title": {"id": "tt0111161", "primaryTitle": "The Shawshank Redemption"},
                "category": "director",
                "characters": [],
            }
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/names/{NAME_ID}/filmography").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.names.get_filmography(NAME_ID)
    assert isinstance(result, ListNameFilmographyResponse)
    assert result.credits[0].category == "director"
    assert result.credits[0].title is not None
    assert result.credits[0].title.id == "tt0111161"


# ---------------------------------------------------------------------------
# get_relationships()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_relationships(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "relationships": [
            {
                "name": {"id": "nm0001000", "displayName": "Jane Doe"},
                "relationType": "spouse",
                "attributes": ["2000-2010"],
            }
        ]
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/names/{NAME_ID}/relationships").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.names.get_relationships(NAME_ID)
    assert isinstance(result, ListNameRelationshipsResponse)
    assert result.relationships[0].relation_type == "spouse"
    assert result.relationships[0].name is not None
    assert result.relationships[0].name.display_name == "Jane Doe"


# ---------------------------------------------------------------------------
# get_trivia()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_trivia(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "triviaEntries": [
            {
                "id": "tr0001",
                "text": "He was born in France to Hungarian parents.",
                "interestCount": 42,
                "voteCount": 100,
            }
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/names/{NAME_ID}/trivia").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.names.get_trivia(NAME_ID)
    assert isinstance(result, ListNameTriviaResponse)
    assert result.trivia_entries[0].interest_count == 42
