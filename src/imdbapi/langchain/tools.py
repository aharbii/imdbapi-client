"""Typed LangChain tools wrapping every major imdbapi.dev endpoint.

Each tool is a :class:`~langchain_core.tools.BaseTool` subclass with:

- A carefully crafted ``description`` — the LLM reads this to decide *when*
  to call the tool.
- A Pydantic ``args_schema`` — enforces correct input types.
- An async ``_arun`` implementation — delegates to the ``IMDBAPIClient``.
- A sync ``_run`` that raises :exc:`NotImplementedError` to encourage async
  usage.  Call ``asyncio.run(tool.arun(...))`` for sync contexts.

Usage::

    from imdbapi import IMDBAPIClient
    from imdbapi.langchain.tools import create_imdb_tools

    async with IMDBAPIClient() as client:
        tools = create_imdb_tools(client)

    # Register with any LangChain / LangGraph agent:
    agent = create_react_agent(llm, tools)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from ..exceptions import IMDBAPIError
from ..models.title import SortBy, SortOrder, TitleType

if TYPE_CHECKING:
    from ..client import IMDBAPIClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dumps(obj: Any) -> str:
    """Serialize a Pydantic model or plain dict to a compact JSON string."""
    if hasattr(obj, "model_dump"):
        return json.dumps(obj.model_dump(exclude_none=True), default=str)
    return json.dumps(obj, default=str)


def _error(exc: Exception) -> str:
    return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _SearchTitlesIn(BaseModel):
    query: str = Field(description="Keywords to search for (title name, actor, etc.)")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of results (1-50)")


class _GetTitleIn(BaseModel):
    title_id: str = Field(
        description="IMDb title ID in the format 'tt' followed by 7 digits, e.g. 'tt0111161'"
    )


class _ListTitlesIn(BaseModel):
    types: list[str] | None = Field(
        default=None,
        description=(
            "Filter by title type. Allowed values: MOVIE, TV_SERIES, TV_MINI_SERIES, "
            "TV_SPECIAL, TV_MOVIE, SHORT, VIDEO, VIDEO_GAME"
        ),
    )
    genres: list[str] | None = Field(
        default=None, description="Filter by genre strings, e.g. ['Action', 'Drama']"
    )
    start_year: int | None = Field(default=None, description="Earliest release year (inclusive)")
    end_year: int | None = Field(default=None, description="Latest release year (inclusive)")
    min_aggregate_rating: float | None = Field(
        default=None, description="Minimum IMDb rating (0.0-10.0)"
    )
    max_aggregate_rating: float | None = Field(
        default=None, description="Maximum IMDb rating (0.0-10.0)"
    )
    min_vote_count: int | None = Field(default=None, description="Minimum number of user votes")
    sort_by: str | None = Field(
        default=None,
        description=(
            "Sort field. Allowed values: SORT_BY_POPULARITY, SORT_BY_RELEASE_DATE, "
            "SORT_BY_USER_RATING, SORT_BY_USER_RATING_COUNT, SORT_BY_YEAR"
        ),
    )
    sort_order: str | None = Field(default=None, description="Sort direction: ASC or DESC")


class _GetTitleCreditsIn(BaseModel):
    title_id: str = Field(description="IMDb title ID (e.g. 'tt0111161')")
    categories: list[str] | None = Field(
        default=None,
        description="Filter by role category, e.g. ['actor', 'director', 'writer']",
    )
    page_size: int | None = Field(default=20, ge=1, le=50, description="Results per page")


class _GetTitleEpisodesIn(BaseModel):
    title_id: str = Field(description="IMDb title ID of the TV series (e.g. 'tt0903747')")
    season: str | None = Field(default=None, description="Filter by season number string, e.g. '1'")
    page_size: int | None = Field(default=20, ge=1, le=50, description="Results per page")


class _GetTitleBoxOfficeIn(BaseModel):
    title_id: str = Field(description="IMDb title ID (e.g. 'tt1375666')")


class _GetTitleAwardsIn(BaseModel):
    title_id: str = Field(description="IMDb title ID (e.g. 'tt0111161')")
    page_size: int | None = Field(default=20, ge=1, le=50, description="Results per page")


class _GetNameIn(BaseModel):
    name_id: str = Field(
        description="IMDb person ID in the format 'nm' followed by 7 digits, e.g. 'nm0000129'"
    )


class _GetNameFilmographyIn(BaseModel):
    name_id: str = Field(description="IMDb person ID (e.g. 'nm0000129')")
    categories: list[str] | None = Field(
        default=None,
        description="Filter by role, e.g. ['actor', 'director', 'producer']",
    )
    page_size: int | None = Field(default=20, ge=1, le=50, description="Results per page")


class _GetInterestCategoryIn(BaseModel):
    interest_id: str = Field(description="IMDb interest/genre ID, e.g. 'ge0000007'")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class SearchTitlesTool(BaseTool):
    """Search IMDb titles by keyword — the primary entry point for any title lookup."""

    name: str = "search_titles"
    description: str = (
        "Search IMDb for movies, TV shows, mini-series, or any other title by keyword. "
        "Returns a list of matching titles with their IMDb IDs, types, years, and ratings. "
        "Use this as the FIRST step when the user mentions a title by name. "
        "The returned 'id' field (e.g. 'tt0111161') is required by all other title tools."
    )
    args_schema: type[BaseModel] = _SearchTitlesIn
    client: Any  # IMDBAPIClient — typed as Any to avoid heavy import

    async def _arun(self, query: str, limit: int = 5) -> str:
        """Search titles by keyword.

        Parameters
        ----------
        query:
            Search keywords.
        limit:
            Maximum number of results to return.

        Returns
        -------
        str
            JSON string with a list of matching title summaries.
        """
        try:
            result = await self.client.search.titles(query, limit=limit)
            titles = [
                {
                    "id": t.id,
                    "primaryTitle": t.primary_title,
                    "type": t.type,
                    "startYear": t.start_year,
                    "rating": t.rating.aggregate_rating if t.rating else None,
                    "voteCount": t.rating.vote_count if t.rating else None,
                    "plot": t.plot,
                }
                for t in result.titles
            ]
            return json.dumps({"titles": titles, "count": len(titles)})
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetTitleTool(BaseTool):
    """Fetch full details for a single IMDb title by its ID."""

    name: str = "get_title"
    description: str = (
        "Fetch complete information for a specific movie or TV show using its IMDb ID. "
        "Returns: full title, type, year, runtime, genres, plot/synopsis, IMDb rating, "
        "Metacritic score, director(s), writer(s), top-billed stars, origin country, "
        "spoken languages, and interest/genre tags. "
        "Use this after 'search_titles' to get detailed information about a specific title. "
        "Required input: an IMDb title ID like 'tt0111161'."
    )
    args_schema: type[BaseModel] = _GetTitleIn
    client: Any

    async def _arun(self, title_id: str) -> str:
        """Get full title details.

        Parameters
        ----------
        title_id:
            IMDb title ID (format: ``tt1234567``).

        Returns
        -------
        str
            JSON string with the complete title record.
        """
        try:
            t = await self.client.titles.get(title_id)
            data = {
                "id": t.id,
                "primaryTitle": t.primary_title,
                "originalTitle": t.original_title,
                "type": t.type,
                "isAdult": t.is_adult,
                "startYear": t.start_year,
                "endYear": t.end_year,
                "runtimeMinutes": round(t.runtime_seconds / 60) if t.runtime_seconds else None,
                "genres": t.genres,
                "plot": t.plot,
                "rating": (
                    {
                        "score": t.rating.aggregate_rating,
                        "votes": t.rating.vote_count,
                    }
                    if t.rating
                    else None
                ),
                "metacritic": (
                    {"score": t.metacritic.score, "reviews": t.metacritic.review_count}
                    if t.metacritic
                    else None
                ),
                "directors": [{"id": d.id, "name": d.display_name} for d in t.directors],
                "writers": [{"id": w.id, "name": w.display_name} for w in t.writers],
                "stars": [{"id": s.id, "name": s.display_name} for s in t.stars],
                "originCountries": [c.name for c in t.origin_countries],
                "spokenLanguages": [lang.name for lang in t.spoken_languages],
                "interests": [i.name for i in t.interests],
            }
            return json.dumps(data, default=str)
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class ListTitlesTool(BaseTool):
    """Browse and filter IMDb titles by genre, year, rating, type, etc."""

    name: str = "list_titles"
    description: str = (
        "Browse IMDb titles with optional filters. Useful when the user asks for "
        "recommendations or wants to discover titles based on criteria rather than a "
        "specific name. "
        "Filters: title type (MOVIE, TV_SERIES, …), genres, release year range, "
        "rating range, vote count, and sort order. "
        "Examples: 'best sci-fi movies of the 90s', 'top-rated TV shows', "
        "'horror movies rated above 7'."
    )
    args_schema: type[BaseModel] = _ListTitlesIn
    client: Any

    async def _arun(  # noqa: PLR0913
        self,
        types: list[str] | None = None,
        genres: list[str] | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        min_aggregate_rating: float | None = None,
        max_aggregate_rating: float | None = None,
        min_vote_count: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> str:
        """List/filter titles with optional criteria.

        Parameters
        ----------
        types:
            Title type codes.
        genres:
            Genre name strings.
        start_year / end_year:
            Release year range.
        min_aggregate_rating / max_aggregate_rating:
            IMDb rating range.
        min_vote_count:
            Minimum user votes.
        sort_by / sort_order:
            Sorting specification.

        Returns
        -------
        str
            JSON string with matching titles.
        """
        try:
            parsed_types = [TitleType(t) for t in types] if types else None
            parsed_sort_by = SortBy(sort_by) if sort_by else None
            parsed_sort_order = SortOrder(sort_order) if sort_order else None

            result = await self.client.titles.list(
                types=parsed_types,
                genres=genres,
                start_year=start_year,
                end_year=end_year,
                min_aggregate_rating=min_aggregate_rating,
                max_aggregate_rating=max_aggregate_rating,
                min_vote_count=min_vote_count,
                sort_by=parsed_sort_by,
                sort_order=parsed_sort_order,
            )
            titles = [
                {
                    "id": t.id,
                    "primaryTitle": t.primary_title,
                    "type": t.type,
                    "startYear": t.start_year,
                    "genres": t.genres,
                    "rating": t.rating.aggregate_rating if t.rating else None,
                }
                for t in result.titles
            ]
            return json.dumps(
                {"titles": titles, "totalCount": result.total_count},
                default=str,
            )
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetTitleCreditsTool(BaseTool):
    """Fetch the full cast and crew list for a title."""

    name: str = "get_title_credits"
    description: str = (
        "Fetch the complete cast and crew credits for a movie or TV show. "
        "Returns each person's IMDb ID, name, role category (actor, director, producer, …), "
        "and any character names they played. "
        "Use this when the user asks 'who acted in X', 'who produced X', or wants a "
        "full cast list beyond the top-billed stars returned by 'get_title'."
    )
    args_schema: type[BaseModel] = _GetTitleCreditsIn
    client: Any

    async def _arun(
        self,
        title_id: str,
        categories: list[str] | None = None,
        page_size: int | None = 20,
    ) -> str:
        """Get cast and crew credits.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        categories:
            Optional role filter.
        page_size:
            Results per page.

        Returns
        -------
        str
            JSON string listing credits.
        """
        try:
            result = await self.client.titles.get_credits(
                title_id, categories=categories, page_size=page_size
            )
            credits = [
                {
                    "nameId": c.name.id if c.name else None,
                    "name": c.name.display_name if c.name else None,
                    "category": c.category,
                    "characters": c.characters,
                    "episodeCount": c.episode_count,
                }
                for c in result.credits
            ]
            return json.dumps({"credits": credits, "totalCount": result.total_count}, default=str)
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetTitleEpisodesTool(BaseTool):
    """List episodes of a TV series, optionally filtered by season."""

    name: str = "get_title_episodes"
    description: str = (
        "List episodes of a TV series with ratings and air dates. "
        "Optionally filter by season number. "
        "Use this when the user asks about specific seasons/episodes, "
        "wants to know episode counts, or needs episode-level ratings. "
        "Only works for TV_SERIES and TV_MINI_SERIES titles."
    )
    args_schema: type[BaseModel] = _GetTitleEpisodesIn
    client: Any

    async def _arun(
        self,
        title_id: str,
        season: str | None = None,
        page_size: int | None = 20,
    ) -> str:
        """Get episodes, optionally filtered by season.

        Parameters
        ----------
        title_id:
            IMDb TV series title ID.
        season:
            Season number string (e.g. ``"1"``).
        page_size:
            Results per page.

        Returns
        -------
        str
            JSON string listing episodes.
        """
        try:
            result = await self.client.titles.get_episodes(
                title_id, season=season, page_size=page_size
            )
            episodes = [
                {
                    "id": ep.id,
                    "title": ep.title,
                    "season": ep.season,
                    "episode": ep.episode_number,
                    "rating": ep.rating.aggregate_rating if ep.rating else None,
                    "plot": ep.plot,
                    "airDate": ep.release_date.model_dump() if ep.release_date else None,
                }
                for ep in result.episodes
            ]
            return json.dumps({"episodes": episodes, "totalCount": result.total_count}, default=str)
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetTitleBoxOfficeTool(BaseTool):
    """Retrieve box-office financial data for a movie."""

    name: str = "get_title_box_office"
    description: str = (
        "Retrieve financial performance data for a movie: "
        "domestic gross revenue, worldwide gross revenue, opening-weekend gross, "
        "and production budget (all with currency codes). "
        "Use this when the user asks about box office performance, revenue, budget, "
        "or how much a movie made."
    )
    args_schema: type[BaseModel] = _GetTitleBoxOfficeIn
    client: Any

    async def _arun(self, title_id: str) -> str:
        """Get box office data.

        Parameters
        ----------
        title_id:
            IMDb title ID.

        Returns
        -------
        str
            JSON string with revenue and budget figures.
        """
        try:
            bo = await self.client.titles.get_box_office(title_id)

            def fmt(money: Any) -> dict[str, Any] | None:
                return {"amount": money.amount, "currency": money.currency} if money else None

            return json.dumps(
                {
                    "domesticGross": fmt(bo.domestic_gross),
                    "worldwideGross": fmt(bo.worldwide_gross),
                    "openingWeekendGross": (
                        {
                            "gross": fmt(bo.opening_weekend_gross.gross),
                            "weekendEndDate": (
                                bo.opening_weekend_gross.weekend_end_date.model_dump()
                                if bo.opening_weekend_gross.weekend_end_date
                                else None
                            ),
                        }
                        if bo.opening_weekend_gross
                        else None
                    ),
                    "productionBudget": fmt(bo.production_budget),
                },
                default=str,
            )
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetTitleAwardsTool(BaseTool):
    """Fetch award nominations and wins for a title."""

    name: str = "get_title_awards"
    description: str = (
        "Fetch award nomination records for a movie or TV show. "
        "Returns total nomination count, win count, and details per nomination including "
        "the award event name (e.g. Academy Awards, Golden Globes), year, category, "
        "and whether it won. "
        "Use this when the user asks 'did X win any Oscars?', 'how many awards did X win?', "
        "or 'what awards was X nominated for?'."
    )
    args_schema: type[BaseModel] = _GetTitleAwardsIn
    client: Any

    async def _arun(self, title_id: str, page_size: int | None = 20) -> str:
        """Get award nomination data.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        page_size:
            Results per page.

        Returns
        -------
        str
            JSON string with nomination stats and individual records.
        """
        try:
            result = await self.client.titles.get_award_nominations(title_id, page_size=page_size)
            nominations = [
                {
                    "event": n.event.name if n.event else None,
                    "year": n.year,
                    "category": n.category,
                    "isWinner": n.is_winner,
                    "nominees": [p.display_name for p in n.nominees],
                    "description": n.text,
                }
                for n in result.award_nominations
            ]
            return json.dumps(
                {
                    "stats": result.stats.model_dump() if result.stats else None,
                    "nominations": nominations,
                },
                default=str,
            )
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetNameTool(BaseTool):
    """Fetch full biographical details for an IMDb person by their name ID."""

    name: str = "get_name"
    description: str = (
        "Fetch complete biographical information about a person (actor, director, writer, …). "
        "Returns: full name, birth date, birth place, death date (if applicable), "
        "biography, height, primary professions, and current IMDb StarMeter rank. "
        "Required input: an IMDb name ID like 'nm0000129'. "
        "Tip: name IDs appear in the 'directors', 'writers', and 'stars' fields "
        "returned by 'get_title'."
    )
    args_schema: type[BaseModel] = _GetNameIn
    client: Any

    async def _arun(self, name_id: str) -> str:
        """Get person biography.

        Parameters
        ----------
        name_id:
            IMDb person ID (format: ``nm1234567``).

        Returns
        -------
        str
            JSON string with biographical information.
        """
        try:
            p = await self.client.names.get(name_id)
            return json.dumps(
                {
                    "id": p.id,
                    "displayName": p.display_name,
                    "alternativeNames": p.alternative_names,
                    "primaryProfessions": p.primary_professions,
                    "biography": p.biography,
                    "heightCm": p.height_cm,
                    "birthName": p.birth_name,
                    "birthDate": p.birth_date.model_dump() if p.birth_date else None,
                    "birthLocation": p.birth_location,
                    "deathDate": p.death_date.model_dump() if p.death_date else None,
                    "deathLocation": p.death_location,
                    "deathReason": p.death_reason,
                    "starMeterRank": (p.meter_ranking.current_rank if p.meter_ranking else None),
                },
                default=str,
            )
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetNameFilmographyTool(BaseTool):
    """Fetch a person's full filmography (acting, directing, writing credits)."""

    name: str = "get_name_filmography"
    description: str = (
        "Fetch the complete filmography (credits) for a person. "
        "Returns each credit with title ID, title name, the person's role category "
        "(actor, director, writer, …), any character names, and episode count for TV. "
        "Use this when the user asks 'what movies has X been in?', "
        "'what did X direct?', or wants a person's complete body of work."
    )
    args_schema: type[BaseModel] = _GetNameFilmographyIn
    client: Any

    async def _arun(
        self,
        name_id: str,
        categories: list[str] | None = None,
        page_size: int | None = 20,
    ) -> str:
        """Get person filmography.

        Parameters
        ----------
        name_id:
            IMDb person ID.
        categories:
            Optional role filter (e.g. ``["actor", "director"]``).
        page_size:
            Results per page.

        Returns
        -------
        str
            JSON string listing credits.
        """
        try:
            result = await self.client.names.get_filmography(
                name_id, categories=categories, page_size=page_size
            )
            credits = [
                {
                    "titleId": c.title.id if c.title else None,
                    "title": c.title.primary_title if c.title else None,
                    "year": c.title.start_year if c.title else None,
                    "category": c.category,
                    "characters": c.characters,
                    "episodeCount": c.episode_count,
                }
                for c in result.credits
            ]
            return json.dumps({"credits": credits, "totalCount": result.total_count}, default=str)
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class ListInterestCategoriesTool(BaseTool):
    """List all IMDb interest/genre categories and their IDs."""

    name: str = "list_interest_categories"
    description: str = (
        "Fetch the complete IMDb interest/genre taxonomy: all top-level categories "
        "and the interest IDs within each. "
        "Useful when you need an exact interest ID to filter 'list_titles', "
        "or when the user asks 'what genres does IMDb have?'. "
        "Returns category names and the ID+name of each interest within them."
    )
    args_schema: type[BaseModel] = BaseModel
    client: Any

    async def _arun(self) -> str:
        """List all interest categories.

        Returns
        -------
        str
            JSON string with all genre categories.
        """
        try:
            result = await self.client.interests.list_categories()
            categories = [
                {
                    "category": cat.category,
                    "interests": [{"id": i.id, "name": i.name} for i in cat.interests],
                }
                for cat in result.categories
            ]
            return json.dumps({"categories": categories}, default=str)
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


class GetInterestCategoryTool(BaseTool):
    """Fetch details and similar interests for a specific IMDb interest/genre."""

    name: str = "get_interest"
    description: str = (
        "Fetch full details for a specific IMDb interest/genre by its ID. "
        "Returns the genre name, description, whether it is a subgenre, "
        "and a list of similar/related interests. "
        "Use 'list_interest_categories' first to discover valid interest IDs."
    )
    args_schema: type[BaseModel] = _GetInterestCategoryIn
    client: Any

    async def _arun(self, interest_id: str) -> str:
        """Get a single interest/genre.

        Parameters
        ----------
        interest_id:
            IMDb interest ID.

        Returns
        -------
        str
            JSON string with interest details.
        """
        try:
            result = await self.client.interests.get(interest_id)
            return json.dumps(
                {
                    "id": result.id,
                    "name": result.name,
                    "description": result.description,
                    "isSubgenre": result.is_subgenre,
                    "similarInterests": [
                        {"id": i.id, "name": i.name} for i in result.similar_interests
                    ],
                },
                default=str,
            )
        except IMDBAPIError as exc:
            return _error(exc)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use the async interface: await tool.arun(...)")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_imdb_tools(client: IMDBAPIClient) -> list[BaseTool]:
    """Create all IMDb LangChain tools bound to a single client instance.

    Parameters
    ----------
    client:
        An open :class:`~imdbapi.client.IMDBAPIClient` instance.

    Returns
    -------
    list[BaseTool]
        A list of tools ready to be registered with a LangChain / LangGraph agent.

    Example
    -------
    ::

        async with IMDBAPIClient() as client:
            tools = create_imdb_tools(client)
            agent = create_react_agent(llm, tools)
    """
    return [
        SearchTitlesTool(client=client),
        GetTitleTool(client=client),
        ListTitlesTool(client=client),
        GetTitleCreditsTool(client=client),
        GetTitleEpisodesTool(client=client),
        GetTitleBoxOfficeTool(client=client),
        GetTitleAwardsTool(client=client),
        GetNameTool(client=client),
        GetNameFilmographyTool(client=client),
        ListInterestCategoriesTool(client=client),
        GetInterestCategoryTool(client=client),
    ]
