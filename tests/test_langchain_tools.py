"""Tests for langchain tools."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from imdbapi.exceptions import IMDBAPIError
from imdbapi.langchain.tools import (
    GetInterestCategoryTool,
    GetNameFilmographyTool,
    GetNameTool,
    GetTitleAwardsTool,
    GetTitleBoxOfficeTool,
    GetTitleCertificatesTool,
    GetTitleCreditsTool,
    GetTitleEpisodesTool,
    GetTitleParentalGuideTool,
    GetTitleTool,
    ListInterestCategoriesTool,
    ListTitlesTool,
    SearchTitlesTool,
    _dumps,
    _error,
    create_imdb_tools,
)


@pytest.fixture
def client() -> MagicMock:
    m = MagicMock()
    m.search = MagicMock()
    m.search.titles = AsyncMock()
    m.titles = MagicMock()
    m.titles.get = AsyncMock()
    m.titles.list = AsyncMock()
    m.titles.get_credits = AsyncMock()
    m.titles.get_episodes = AsyncMock()
    m.titles.get_box_office = AsyncMock()
    m.titles.get_award_nominations = AsyncMock()
    m.titles.get_parents_guide = AsyncMock()
    m.titles.get_certificates = AsyncMock()
    m.names = MagicMock()
    m.names.get = AsyncMock()
    m.names.get_filmography = AsyncMock()
    m.interests = MagicMock()
    m.interests.list_categories = AsyncMock()
    m.interests.get = AsyncMock()
    m.charts = MagicMock()
    return m


def test_create_imdb_tools(client: MagicMock) -> None:
    tools = create_imdb_tools(client)
    assert len(tools) == 13


def test_dumps() -> None:
    class Dummy(BaseModel):
        a: int

    assert _dumps({"a": 1}) == '{"a": 1}'
    assert _dumps(Dummy(a=1)) == '{"a": 1}'


def test_error() -> None:
    assert _error(Exception("test")) == '{"error": "test"}'


@pytest.mark.asyncio
async def test_search_titles_tool(client: MagicMock) -> None:
    tool = SearchTitlesTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(query="test")

    t1 = MagicMock(
        id="tt1",
        primary_title="1",
        type="movie",
        start_year=2020,
        rating=MagicMock(aggregate_rating=8.0, vote_count=100),
        plot="p",
    )
    t2 = MagicMock(
        id="tt2", primary_title="2", type="movie", start_year=2020, rating=None, plot="p"
    )
    client.search.titles.return_value = MagicMock(titles=[t1, t2])
    result = await tool._arun(query="test")
    assert "count" in result

    client.search.titles.side_effect = IMDBAPIError("error")
    result = await tool._arun(query="test")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_title_tool(client: MagicMock) -> None:
    tool = GetTitleTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(title_id="tt123")

    t1 = MagicMock(
        id="tt1",
        primary_title="1",
        original_title="1",
        type="movie",
        is_adult=False,
        start_year=2020,
        end_year=2021,
        runtime_seconds=120,
        genres=["A"],
        plot="p",
        rating=MagicMock(aggregate_rating=8.0, vote_count=100),
        metacritic=MagicMock(score=80, review_count=20),
        directors=[MagicMock(id="nm1", display_name="D1")],
        writers=[],
        stars=[],
        origin_countries=[MagicMock(name="US")],
        spoken_languages=[],
        interests=[],
    )
    client.titles.get.return_value = t1
    result = await tool._arun(title_id="tt123")
    assert result is not None

    t2 = MagicMock(
        id="tt1",
        primary_title="1",
        original_title="1",
        type="movie",
        is_adult=False,
        start_year=2020,
        end_year=2021,
        runtime_seconds=None,
        genres=["A"],
        plot="p",
        rating=None,
        metacritic=None,
        directors=[],
        writers=[],
        stars=[],
        origin_countries=[],
        spoken_languages=[],
        interests=[],
    )
    client.titles.get.return_value = t2
    result = await tool._arun(title_id="tt123")
    assert result is not None

    client.titles.get.side_effect = IMDBAPIError("error")
    result = await tool._arun(title_id="tt123")
    assert "error" in result


@pytest.mark.asyncio
async def test_list_titles_tool(client: MagicMock) -> None:
    tool = ListTitlesTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run()

    t1 = MagicMock(
        id="tt1",
        primary_title="1",
        type="movie",
        start_year=2020,
        rating=MagicMock(aggregate_rating=8.0, vote_count=100),
        plot="p",
    )
    t2 = MagicMock(
        id="tt2", primary_title="2", type="movie", start_year=2020, rating=None, plot="p"
    )
    client.titles.list.return_value = MagicMock(titles=[t1, t2])
    result = await tool._arun()
    assert "count" in result

    client.titles.list.side_effect = IMDBAPIError("error")
    result = await tool._arun()
    assert "error" in result


@pytest.mark.asyncio
async def test_get_title_credits_tool(client: MagicMock) -> None:
    tool = GetTitleCreditsTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(title_id="tt123")

    class MockName:
        def __init__(self, id: str, display_name: str) -> None:
            self.id = id
            self.display_name = display_name

    class MockCredit:
        def __init__(
            self, category: str, characters: list[str], episode_count: int | None, name: MockName
        ) -> None:
            self.category = category
            self.characters = characters
            self.episode_count = episode_count
            self.name = name

    c1 = MockCredit("actor", ["C1"], 10, MockName("nm1", "N1"))
    c2 = MockCredit("director", [], None, MockName("nm2", "N2"))

    m_res = MagicMock(credits=[c1, c2])
    m_res.total_count = 2
    client.titles.get_credits.return_value = m_res
    result = await tool._arun(title_id="tt123")
    assert "credits" in result

    client.titles.get_credits.side_effect = IMDBAPIError("error")
    result = await tool._arun(title_id="tt123")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_title_episodes_tool(client: MagicMock) -> None:
    tool = GetTitleEpisodesTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(title_id="tt123")

    e1 = MagicMock(
        id="tt2",
        primary_title="Ep 1",
        season_number=1,
        episode_number=1,
        release_year=2020,
        rating=MagicMock(aggregate_rating=8.0, vote_count=100),
        plot="p",
    )
    e2 = MagicMock(
        id="tt3",
        primary_title="Ep 2",
        season_number=1,
        episode_number=2,
        release_year=2020,
        rating=None,
        plot="p",
    )
    client.titles.get_episodes.return_value = MagicMock(episodes=[e1, e2])
    result = await tool._arun(title_id="tt123")
    assert "count" in result

    client.titles.get_episodes.side_effect = IMDBAPIError("error")
    result = await tool._arun(title_id="tt123")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_title_box_office_tool(client: MagicMock) -> None:
    tool = GetTitleBoxOfficeTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(title_id="tt123")

    b = MagicMock(
        budget=MagicMock(amount=100, currency="USD"),
        worldwide=MagicMock(amount=200, currency="USD"),
        domestic=MagicMock(amount=50, currency="USD"),
        opening_weekend=MagicMock(amount=10, currency="USD"),
    )
    client.titles.get_box_office.return_value = b
    result = await tool._arun(title_id="tt123")
    assert result is not None

    b2 = MagicMock(budget=None, worldwide=None, domestic=None, opening_weekend=None)
    client.titles.get_box_office.return_value = b2
    result = await tool._arun(title_id="tt123")
    assert result is not None

    client.titles.get_box_office.side_effect = IMDBAPIError("error")
    result = await tool._arun(title_id="tt123")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_title_awards_tool(client: MagicMock) -> None:
    tool = GetTitleAwardsTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(title_id="tt123")

    a1 = MagicMock(event_name="Oscars", category="Best Picture", is_winner=True, text="p")
    a1.nominees = [MagicMock(display_name="N1")]
    stats = MagicMock()
    stats.model_dump.return_value = {"total_nominations": 1}
    client.titles.get_award_nominations.return_value = MagicMock(
        stats=stats, award_nominations=[a1]
    )
    result = await tool._arun(title_id="tt123")
    assert "nominations" in result

    client.titles.get_award_nominations.side_effect = IMDBAPIError("error")
    result = await tool._arun(title_id="tt123")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_name_tool(client: MagicMock) -> None:
    tool = GetNameTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(name_id="nm123")

    n1 = MagicMock(
        id="nm1",
        display_name="N1",
        real_name="N 1",
        birth_date=MagicMock(date="2000-01-01"),
        death_date=MagicMock(date="2020-01-01"),
        height_centimeters=180,
        bio="b",
    )
    client.names.get.return_value = n1
    result = await tool._arun(name_id="nm123")
    assert result is not None

    n2 = MagicMock(
        id="nm1",
        display_name="N1",
        real_name="N 1",
        birth_date=None,
        death_date=None,
        height_centimeters=None,
        bio="b",
    )
    client.names.get.return_value = n2
    result = await tool._arun(name_id="nm123")
    assert result is not None

    client.names.get.side_effect = IMDBAPIError("error")
    result = await tool._arun(name_id="nm123")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_name_filmography_tool(client: MagicMock) -> None:
    tool = GetNameFilmographyTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(name_id="nm123")

    c1 = MagicMock(
        title=MagicMock(id="tt1", primary_title="T1", type="movie", start_year=2020),
        category="actor",
        characters=["C1"],
        episode_count=10,
    )
    c2 = MagicMock(
        title=MagicMock(id="tt2", primary_title="T2", type="movie", start_year=2020),
        category="director",
        characters=[],
        episode_count=None,
    )
    client.names.get_filmography.return_value = MagicMock(credits=[c1, c2])
    result = await tool._arun(name_id="nm123")
    assert "count" in result

    client.names.get_filmography.side_effect = IMDBAPIError("error")
    result = await tool._arun(name_id="nm123")
    assert "error" in result


@pytest.mark.asyncio
async def test_list_interest_categories_tool(client: MagicMock) -> None:
    tool = ListInterestCategoriesTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run()

    client.interests.list_categories.return_value = MagicMock(
        model_dump=MagicMock(return_value={"categories": []})
    )
    result = await tool._arun()
    assert result is not None

    client.interests.list_categories.side_effect = IMDBAPIError("error")
    result = await tool._arun()
    assert "error" in result


@pytest.mark.asyncio
async def test_get_interest_category_tool(client: MagicMock) -> None:
    tool = GetInterestCategoryTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(interest_id="in123")

    client.interests.get.return_value = MagicMock(
        model_dump=MagicMock(return_value={"id": "in123"})
    )
    result = await tool._arun(interest_id="in123")
    assert result is not None

    client.interests.get.side_effect = IMDBAPIError("error")
    result = await tool._arun(interest_id="in123")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_title_parental_guide_tool(client: MagicMock) -> None:
    tool = GetTitleParentalGuideTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(title_id="tt123")

    pg = MagicMock(category="violence")
    sev = MagicMock(severity_level="Severe", vote_count=10)
    rev = MagicMock(is_spoiler=False, text="text")
    pg.severity_breakdowns = [sev]
    pg.reviews = [rev]
    client.titles.get_parents_guide.return_value = MagicMock(parents_guide=[pg])
    result = await tool._arun(title_id="tt123")
    assert result is not None

    client.titles.get_parents_guide.side_effect = IMDBAPIError("error")
    result = await tool._arun(title_id="tt123")
    assert "error" in result


@pytest.mark.asyncio
async def test_get_title_certificates_tool(client: MagicMock) -> None:
    tool = GetTitleCertificatesTool(client=client)
    with pytest.raises(NotImplementedError):
        tool._run(title_id="tt123")

    client.titles.get_certificates.return_value = MagicMock(
        model_dump=MagicMock(return_value={"certificates": []})
    )
    result = await tool._arun(title_id="tt123")
    assert result is not None

    client.titles.get_certificates.side_effect = IMDBAPIError("error")
    result = await tool._arun(title_id="tt123")
    assert "error" in result
