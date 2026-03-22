"""Tests for the async pagination iterator."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from imdbapi.client import IMDBAPIClient
from imdbapi.models import ListTitlesResponse

BASE_URL = "https://api.imdbapi.dev"


@pytest.fixture
def client() -> IMDBAPIClient:
    return IMDBAPIClient(base_url=BASE_URL, max_retries=1)


def _title(idx: int) -> dict[str, Any]:
    return {
        "id": f"tt{idx:07d}",
        "type": "MOVIE",
        "isAdult": False,
        "primaryTitle": f"Movie {idx}",
        "startYear": 2020,
        "genres": [],
        "rating": {"aggregateRating": 7.0, "voteCount": 1000},
        "directors": [],
        "stars": [],
        "writers": [],
        "originCountries": [],
        "spokenLanguages": [],
        "interests": [],
    }


# ---------------------------------------------------------------------------
# Single-page iteration (no cursor)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_page_iteration(client: IMDBAPIClient) -> None:
    payload: dict[str, Any] = {
        "titles": [_title(1), _title(2)],
        "totalCount": 2,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(return_value=httpx.Response(200, json=payload))
        pages: list[ListTitlesResponse] = []
        async for page in client.titles.list_pages():
            pages.append(page)
    assert len(pages) == 1
    assert len(pages[0].titles) == 2


# ---------------------------------------------------------------------------
# Multi-page iteration (cursor chain)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_multi_page_iteration(client: IMDBAPIClient) -> None:
    page1: dict[str, Any] = {
        "titles": [_title(1)],
        "totalCount": 2,
        "nextPageToken": "cursor_p2",
    }
    page2: dict[str, Any] = {
        "titles": [_title(2)],
        "totalCount": 2,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(
            side_effect=[
                httpx.Response(200, json=page1),
                httpx.Response(200, json=page2),
            ]
        )
        collected: list[str] = []
        async for page in client.titles.list_pages():
            for title in page.titles:
                collected.append(title.id)
    assert collected == ["tt0000001", "tt0000002"]


# ---------------------------------------------------------------------------
# Episode pagination via get_episodes_pages()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_episodes_pages(client: IMDBAPIClient) -> None:
    ep1: dict[str, Any] = {
        "episodes": [{"id": "tt9000001", "title": "Pilot", "season": "1", "episodeNumber": 1}],
        "totalCount": 2,
        "nextPageToken": "ep_cursor",
    }
    ep2: dict[str, Any] = {
        "episodes": [
            {"id": "tt9000002", "title": "Episode 2", "season": "1", "episodeNumber": 2}
        ],
        "totalCount": 2,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt0903747/episodes").mock(
            side_effect=[
                httpx.Response(200, json=ep1),
                httpx.Response(200, json=ep2),
            ]
        )
        ids: list[str] = []
        async for page in client.titles.get_episodes_pages("tt0903747"):
            for ep in page.episodes:
                ids.append(ep.id)
    assert ids == ["tt9000001", "tt9000002"]


# ---------------------------------------------------------------------------
# StarMeter chart pagination
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_starmeter_pages(client: IMDBAPIClient) -> None:
    p1: dict[str, Any] = {
        "names": [{"id": "nm0001", "displayName": "Person A"}],
        "nextPageToken": "sm_cursor",
    }
    p2: dict[str, Any] = {
        "names": [{"id": "nm0002", "displayName": "Person B"}],
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/chart/starmeter").mock(
            side_effect=[
                httpx.Response(200, json=p1),
                httpx.Response(200, json=p2),
            ]
        )
        names: list[str] = []
        async for page in client.charts.starmeter_pages():
            for person in page.names:
                names.append(person.display_name)
    assert names == ["Person A", "Person B"]
