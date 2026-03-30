"""Shared pytest fixtures and helpers.

All HTTP calls are intercepted by ``respx`` — no real network traffic occurs
during tests.  Each test module receives a pre-configured :class:`IMDBAPIClient`
and a ``respx.MockRouter`` anchored to the API base URL.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pytest
import respx

from imdbapi.client import IMDBAPIClient

BASE_URL = "https://api.imdbapi.dev"


# ---------------------------------------------------------------------------
# Client fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> IMDBAPIClient:
    """Return an ``IMDBAPIClient`` configured for testing (1 retry, no delay)."""
    return IMDBAPIClient(base_url=BASE_URL, max_retries=1, timeout=5.0)


# ---------------------------------------------------------------------------
# RESPX router — intercepts all outgoing httpx calls
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_router() -> Generator[respx.MockRouter]:
    """Yield an active RESPX mock router scoped to the API base URL.

    Usage::

        def test_something(client, mock_router):
            mock_router.get("/titles/tt0111161").mock(
                return_value=httpx.Response(200, json={...})
            )
            result = asyncio.run(client.titles.get("tt0111161"))
    """
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router


# ---------------------------------------------------------------------------
# Canonical sample payloads
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_title_payload() -> dict[str, Any]:
    return {
        "id": "tt0111161",
        "type": "MOVIE",
        "isAdult": False,
        "primaryTitle": "The Shawshank Redemption",
        "originalTitle": "The Shawshank Redemption",
        "primaryImage": {"url": "https://example.com/img.jpg", "width": 1000, "height": 1480},
        "startYear": 1994,
        "endYear": None,
        "runtimeSeconds": 8520,
        "genres": ["Drama"],
        "rating": {"aggregateRating": 9.3, "voteCount": 2_800_000},
        "metacritic": {"url": "https://metacritic.com/foo", "score": 80, "reviewCount": 20},
        "plot": "Two imprisoned men bond over a number of years.",
        "directors": [{"id": "nm0001104", "displayName": "Frank Darabont"}],
        "writers": [{"id": "nm0000126", "displayName": "Stephen King"}],
        "stars": [{"id": "nm0000209", "displayName": "Tim Robbins"}],
        "originCountries": [{"code": "US", "name": "United States"}],
        "spokenLanguages": [{"code": "eng", "name": "English"}],
        "interests": [{"id": "ge0000007", "name": "Drama"}],
    }


@pytest.fixture
def sample_name_payload() -> dict[str, Any]:
    return {
        "id": "nm0001104",
        "displayName": "Frank Darabont",
        "alternativeNames": [],
        "primaryImage": {"url": "https://example.com/fd.jpg", "width": 400, "height": 600},
        "primaryProfessions": ["director", "writer", "producer"],
        "biography": "Frank Darabont is an American filmmaker.",
        "heightCm": 188,
        "birthName": "Frank Árpád Darabont",
        "birthDate": {"year": 1959, "month": 1, "day": 28},
        "birthLocation": "Montbéliard, Doubs, France",
        "meterRanking": {"currentRank": 42, "changeDirection": "UP", "difference": 5},
    }


@pytest.fixture
def sample_interest_payload() -> dict[str, Any]:
    return {
        "id": "ge0000007",
        "name": "Drama",
        "description": "Serious, plot-driven presentations.",
        "isSubgenre": False,
        "similarInterests": [{"id": "ge0000001", "name": "Crime"}],
    }
