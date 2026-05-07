"""Tests for the TitlesEndpoint covering all title operations."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from imdbapi.client import IMDBAPIClient
from imdbapi.exceptions import IMDBAPINotFoundError, IMDBAPIValidationError
from imdbapi.models import (
    BoxOffice,
    ListTitleAKAsResponse,
    ListTitleAwardNominationsResponse,
    ListTitleCertificatesResponse,
    ListTitleCompanyCreditsResponse,
    ListTitleCreditsResponse,
    ListTitleEpisodesResponse,
    ListTitleImagesResponse,
    ListTitleParentsGuideResponse,
    ListTitleReleaseDatesResponse,
    ListTitleSeasonsResponse,
    ListTitlesResponse,
    ListTitleVideosResponse,
    Title,
    TitleType,
)

BASE_URL = "https://api.imdbapi.dev"
TITLE_ID = "tt0111161"


@pytest.fixture
def client() -> IMDBAPIClient:
    return IMDBAPIClient(base_url=BASE_URL, max_retries=1)


@pytest.fixture
def title_payload() -> dict[str, Any]:
    return {
        "id": TITLE_ID,
        "type": "MOVIE",
        "isAdult": False,
        "primaryTitle": "The Shawshank Redemption",
        "startYear": 1994,
        "genres": ["Drama"],
        "rating": {"aggregateRating": 9.3, "voteCount": 2_800_000},
        "directors": [{"id": "nm0001104", "displayName": "Frank Darabont"}],
        "stars": [],
        "writers": [],
        "originCountries": [],
        "spokenLanguages": [],
        "interests": [],
    }


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_title(client: IMDBAPIClient, title_payload: dict[str, Any]) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}").mock(return_value=httpx.Response(200, json=title_payload))
        title = await client.titles.get(TITLE_ID)
    assert isinstance(title, Title)
    assert title.id == TITLE_ID
    assert title.primary_title == "The Shawshank Redemption"
    assert title.type == TitleType.MOVIE
    assert title.start_year == 1994
    assert title.rating is not None
    assert title.rating.aggregate_rating == pytest.approx(9.3)
    assert len(title.directors) == 1
    assert title.directors[0].display_name == "Frank Darabont"


@pytest.mark.asyncio
async def test_get_title_not_found(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt9999999").mock(
            return_value=httpx.Response(404, json={"message": "not found"})
        )
        with pytest.raises(IMDBAPINotFoundError):
            await client.titles.get("tt9999999")


@pytest.mark.asyncio
async def test_get_title_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}").mock(
            return_value=httpx.Response(200, json={"id": TITLE_ID})
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get(TITLE_ID)


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_titles(client: IMDBAPIClient, title_payload: dict[str, Any]) -> None:
    response_payload = {
        "titles": [title_payload],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(return_value=httpx.Response(200, json=response_payload))
        result = await client.titles.list(types=[TitleType.MOVIE])
    assert isinstance(result, ListTitlesResponse)
    assert result.total_count == 1
    assert result.titles[0].id == TITLE_ID
    assert result.next_page_token is None


@pytest.mark.asyncio
async def test_list_titles_with_pagination(
    client: IMDBAPIClient, title_payload: dict[str, Any]
) -> None:
    response_payload = {
        "titles": [title_payload],
        "totalCount": 100,
        "nextPageToken": "cursor_abc",
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(return_value=httpx.Response(200, json=response_payload))
        result = await client.titles.list()
    assert result.next_page_token == "cursor_abc"


# ---------------------------------------------------------------------------
# batch_get()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_get_titles(client: IMDBAPIClient, title_payload: dict[str, Any]) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles:batchGet").mock(
            return_value=httpx.Response(200, json={"titles": [title_payload]})
        )
        result = await client.titles.batch_get([TITLE_ID])
    assert len(result.titles) == 1
    assert result.titles[0].id == TITLE_ID


# ---------------------------------------------------------------------------
# get_credits()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_credits(client: IMDBAPIClient) -> None:
    payload = {
        "credits": [
            {
                "name": {"id": "nm0000209", "displayName": "Tim Robbins"},
                "category": "actor",
                "characters": ["Andy Dufresne"],
            }
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/credits").mock(return_value=httpx.Response(200, json=payload))
        result = await client.titles.get_credits(TITLE_ID)
    assert isinstance(result, ListTitleCreditsResponse)
    assert result.credits[0].category == "actor"
    assert result.credits[0].characters == ["Andy Dufresne"]


@pytest.mark.asyncio
async def test_iter_credits(client: IMDBAPIClient) -> None:
    payload = {
        "credits": [
            {
                "name": {"id": "nm0000209", "displayName": "Tim Robbins"},
                "category": "actor",
                "characters": ["Andy Dufresne"],
            }
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/credits").mock(return_value=httpx.Response(200, json=payload))
        items = []
        async for page in client.titles.get_credits_pages(TITLE_ID):
            items.extend(page.credits)
    assert len(items) == 1
    assert items[0].name is not None
    assert items[0].name.id == "nm0000209"


# ---------------------------------------------------------------------------
# get_release_dates()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_release_dates(client: IMDBAPIClient) -> None:
    payload = {
        "releaseDates": [
            {
                "country": {"code": "US", "name": "United States"},
                "releaseDate": {"year": 1994, "month": 9, "day": 23},
                "attributes": ["Theatrical"],
            }
        ],
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/releaseDates").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.titles.get_release_dates(TITLE_ID)
    assert isinstance(result, ListTitleReleaseDatesResponse)
    assert result.release_dates[0].country is not None
    assert result.release_dates[0].country.code == "US"
    assert result.release_dates[0].release_date is not None
    assert result.release_dates[0].release_date.year == 1994


# ---------------------------------------------------------------------------
# get_akas()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_akas(client: IMDBAPIClient) -> None:
    payload = {
        "akas": [
            {
                "text": "Die Verurteilten",
                "country": {"code": "DE", "name": "Germany"},
                "language": {"code": "deu", "name": "German"},
                "attributes": [],
            }
        ]
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/akas").mock(return_value=httpx.Response(200, json=payload))
        result = await client.titles.get_akas(TITLE_ID)
    assert isinstance(result, ListTitleAKAsResponse)
    assert result.akas[0].text == "Die Verurteilten"


# ---------------------------------------------------------------------------
# get_seasons() / get_episodes()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_seasons(client: IMDBAPIClient) -> None:
    payload = {"seasons": [{"season": "1", "episodeCount": 10}]}
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/seasons").mock(return_value=httpx.Response(200, json=payload))
        result = await client.titles.get_seasons(TITLE_ID)
    assert isinstance(result, ListTitleSeasonsResponse)
    assert result.seasons[0].episode_count == 10


@pytest.mark.asyncio
async def test_get_episodes(client: IMDBAPIClient) -> None:
    payload = {
        "episodes": [
            {
                "id": "tt1000001",
                "title": "Pilot",
                "season": "1",
                "episodeNumber": 1,
                "rating": {"aggregateRating": 8.5, "voteCount": 5000},
            }
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/episodes").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.titles.get_episodes(TITLE_ID, season="1")
    assert isinstance(result, ListTitleEpisodesResponse)
    assert result.episodes[0].title == "Pilot"


# ---------------------------------------------------------------------------
# get_images() / get_videos()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_images(client: IMDBAPIClient) -> None:
    payload = {
        "images": [
            {"url": "https://example.com/img.jpg", "width": 1000, "height": 1480, "type": "poster"}
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/images").mock(return_value=httpx.Response(200, json=payload))
        result = await client.titles.get_images(TITLE_ID)
    assert isinstance(result, ListTitleImagesResponse)
    assert result.images[0].type == "poster"


@pytest.mark.asyncio
async def test_get_videos(client: IMDBAPIClient) -> None:
    payload = {
        "videos": [
            {
                "id": "vi1000001",
                "type": "Trailer",
                "name": "Official Trailer",
                "runtimeSeconds": 120,
            }
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/videos").mock(return_value=httpx.Response(200, json=payload))
        result = await client.titles.get_videos(TITLE_ID)
    assert isinstance(result, ListTitleVideosResponse)
    assert result.videos[0].name == "Official Trailer"


# ---------------------------------------------------------------------------
# get_award_nominations()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_award_nominations(client: IMDBAPIClient) -> None:
    payload = {
        "stats": {"nominationCount": 7, "winCount": 0},
        "awardNominations": [
            {
                "event": {"id": "ev0000003", "name": "Academy Awards"},
                "year": 1995,
                "category": "Best Picture",
                "isWinner": False,
            }
        ],
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/awardNominations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.titles.get_award_nominations(TITLE_ID)
    assert isinstance(result, ListTitleAwardNominationsResponse)
    assert result.stats is not None
    assert result.stats.nomination_count == 7
    assert result.award_nominations[0].is_winner is False


# ---------------------------------------------------------------------------
# get_parents_guide()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_parents_guide(client: IMDBAPIClient) -> None:
    payload = {
        "parentsGuide": [
            {
                "category": "VIOLENCE",
                "severityBreakdowns": [{"severityLevel": "Mild", "voteCount": 100}],
                "reviews": [],
            }
        ]
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/parentsGuide").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.titles.get_parents_guide(TITLE_ID)
    assert isinstance(result, ListTitleParentsGuideResponse)
    assert result.parents_guide[0].severity_breakdowns[0].severity_level == "Mild"


# ---------------------------------------------------------------------------
# get_certificates()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_certificates(client: IMDBAPIClient) -> None:
    payload = {
        "certificates": [
            {"rating": "R", "country": {"code": "US", "name": "United States"}, "attributes": []}
        ],
        "totalCount": 1,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/certificates").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.titles.get_certificates(TITLE_ID)
    assert isinstance(result, ListTitleCertificatesResponse)
    assert result.certificates[0].rating == "R"


# ---------------------------------------------------------------------------
# get_company_credits()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_company_credits(client: IMDBAPIClient) -> None:
    payload = {
        "companyCredits": [
            {
                "company": {"id": "co0001", "name": "Castle Rock Entertainment"},
                "category": "production",
                "countries": [],
                "attributes": [],
            }
        ],
        "totalCount": 1,
        "nextPageToken": None,
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/companyCredits").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.titles.get_company_credits(TITLE_ID)
    assert isinstance(result, ListTitleCompanyCreditsResponse)
    assert result.company_credits[0].company is not None
    assert result.company_credits[0].company.name == "Castle Rock Entertainment"


# ---------------------------------------------------------------------------
# get_box_office()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_box_office(client: IMDBAPIClient) -> None:
    payload = {
        "domesticGross": {"amount": 16_000_000, "currency": "USD"},
        "worldwideGross": {"amount": 58_000_000, "currency": "USD"},
        "openingWeekendGross": {
            "gross": {"amount": 727_327, "currency": "USD"},
            "weekendEndDate": {"year": 1994, "month": 9, "day": 25},
        },
        "productionBudget": {"amount": 25_000_000, "currency": "USD"},
    }
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get(f"/titles/{TITLE_ID}/boxOffice").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = await client.titles.get_box_office(TITLE_ID)
    assert isinstance(result, BoxOffice)
    assert result.worldwide_gross is not None
    assert result.worldwide_gross.amount == 58_000_000
    assert result.worldwide_gross.currency == "USD"
    assert result.opening_weekend_gross is not None
    assert result.opening_weekend_gross.gross is not None
    assert result.opening_weekend_gross.gross.amount == 727_327


@pytest.mark.asyncio
async def test_list_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(return_value=httpx.Response(200, json=["invalid", "data"]))
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.list()


@pytest.mark.asyncio
async def test_batch_get_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles:batchGet?titleIds=tt123").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.batch_get(["tt123"])


@pytest.mark.asyncio
async def test_get_credits_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/credits").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_credits("tt123")


@pytest.mark.asyncio
async def test_get_release_dates_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/releaseDates").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_release_dates("tt123")


@pytest.mark.asyncio
async def test_get_akas_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/akas").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_akas("tt123")


@pytest.mark.asyncio
async def test_get_seasons_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/seasons").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_seasons("tt123")


@pytest.mark.asyncio
async def test_get_episodes_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/episodes?season=1").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_episodes("tt123", season="1")


@pytest.mark.asyncio
async def test_get_images_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/images").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_images("tt123")


@pytest.mark.asyncio
async def test_get_videos_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/videos").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_videos("tt123")


@pytest.mark.asyncio
async def test_get_award_nominations_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/awardNominations").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_award_nominations("tt123")


@pytest.mark.asyncio
async def test_get_parents_guide_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/parentsGuide").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_parents_guide("tt123")


@pytest.mark.asyncio
async def test_get_certificates_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/certificates").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_certificates("tt123")


@pytest.mark.asyncio
async def test_get_company_credits_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/companyCredits").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_company_credits("tt123")


@pytest.mark.asyncio
async def test_get_box_office_validation_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt123/boxOffice").mock(
            return_value=httpx.Response(200, json=["invalid", "data"])
        )
        with pytest.raises(IMDBAPIValidationError):
            await client.titles.get_box_office("tt123")


def test_title_type_missing() -> None:
    from imdbapi.models.title import TitleType

    assert TitleType("movie") == TitleType.MOVIE
    assert TitleType("tvSeries") == TitleType.TV_SERIES
    assert TitleType("tvMiniSeries") == TitleType.TV_MINI_SERIES
    assert TitleType("tvSpecial") == TitleType.TV_SPECIAL
    assert TitleType("tvMovie") == TitleType.TV_MOVIE
    assert TitleType("short") == TitleType.SHORT
    assert TitleType("tvShort") == TitleType.SHORT
    assert TitleType("video") == TitleType.VIDEO
    assert TitleType("videoGame") == TitleType.VIDEO_GAME
    with pytest.raises(ValueError):
        TitleType("unknown")
    assert TitleType._missing_("unknown") is None
    assert TitleType._missing_(123) is None
