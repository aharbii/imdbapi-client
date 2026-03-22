"""Title (movie / TV show) data models.

Covers all response schemas from the ``/titles`` and ``/search/titles``
endpoint families defined in imdbapi.dev v2.7.12.
"""

from __future__ import annotations

from enum import StrEnum

from .common import (
    Company,
    Country,
    Event,
    Image,
    Language,
    Metacritic,
    Money,
    NameRef,
    PrecisionDate,
    Rating,
    _CamelModel,
)
from .interest import InterestRef

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class TitleType(StrEnum):
    """IMDb title type codes."""

    MOVIE = "MOVIE"
    TV_SERIES = "TV_SERIES"
    TV_MINI_SERIES = "TV_MINI_SERIES"
    TV_SPECIAL = "TV_SPECIAL"
    TV_MOVIE = "TV_MOVIE"
    SHORT = "SHORT"
    VIDEO = "VIDEO"
    VIDEO_GAME = "VIDEO_GAME"


class SortBy(StrEnum):
    """Valid ``sortBy`` values for ``GET /titles``."""

    POPULARITY = "SORT_BY_POPULARITY"
    RELEASE_DATE = "SORT_BY_RELEASE_DATE"
    USER_RATING = "SORT_BY_USER_RATING"
    USER_RATING_COUNT = "SORT_BY_USER_RATING_COUNT"
    YEAR = "SORT_BY_YEAR"


class SortOrder(StrEnum):
    """Sort direction."""

    ASC = "ASC"
    DESC = "DESC"


class ParentsGuideCategory(StrEnum):
    """Content advisory categories."""

    SEXUAL_CONTENT = "SEXUAL_CONTENT"
    VIOLENCE = "VIOLENCE"
    PROFANITY = "PROFANITY"
    ALCOHOL_DRUGS = "ALCOHOL_DRUGS"
    FRIGHTENING_INTENSE_SCENES = "FRIGHTENING_INTENSE_SCENES"


# ---------------------------------------------------------------------------
# Abbreviated / embedded references
# ---------------------------------------------------------------------------


class TitleRef(_CamelModel):
    """Abbreviated title reference returned inside credits and episodes."""

    id: str
    primary_title: str | None = None
    type: TitleType | None = None
    start_year: int | None = None


# ---------------------------------------------------------------------------
# Core title object
# ---------------------------------------------------------------------------


class Title(_CamelModel):
    """Full title object returned by ``GET /titles/{titleId}`` and list endpoints."""

    id: str
    type: TitleType | None = None
    is_adult: bool = False
    primary_title: str
    original_title: str | None = None
    primary_image: Image | None = None
    start_year: int | None = None
    end_year: int | None = None
    runtime_seconds: int | None = None
    genres: list[str] = []
    rating: Rating | None = None
    metacritic: Metacritic | None = None
    plot: str | None = None
    directors: list[NameRef] = []
    writers: list[NameRef] = []
    stars: list[NameRef] = []
    origin_countries: list[Country] = []
    spoken_languages: list[Language] = []
    interests: list[InterestRef] = []


# ---------------------------------------------------------------------------
# List / batch responses
# ---------------------------------------------------------------------------


class ListTitlesResponse(_CamelModel):
    """Response from ``GET /titles``."""

    titles: list[Title] = []
    total_count: int = 0
    next_page_token: str | None = None


class BatchGetTitlesResponse(_CamelModel):
    """Response from ``GET /titles:batchGet``."""

    titles: list[Title] = []


# ---------------------------------------------------------------------------
# Credits
# ---------------------------------------------------------------------------


class Credit(_CamelModel):
    """A single credit linking a person to a title."""

    title: TitleRef | None = None
    name: NameRef | None = None
    category: str | None = None
    characters: list[str] = []
    episode_count: int | None = None


class ListTitleCreditsResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/credits``."""

    credits: list[Credit] = []
    total_count: int = 0
    next_page_token: str | None = None


# ---------------------------------------------------------------------------
# Release dates
# ---------------------------------------------------------------------------


class ReleaseDate(_CamelModel):
    """A single regional release date record."""

    country: Country | None = None
    release_date: PrecisionDate | None = None
    attributes: list[str] = []


class ListTitleReleaseDatesResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/releaseDates``."""

    release_dates: list[ReleaseDate] = []
    next_page_token: str | None = None


# ---------------------------------------------------------------------------
# AKAs (alternative titles)
# ---------------------------------------------------------------------------


class AKA(_CamelModel):
    """An alternative / localised title."""

    text: str
    country: Country | None = None
    language: Language | None = None
    attributes: list[str] = []


class ListTitleAKAsResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/akas``."""

    akas: list[AKA] = []


# ---------------------------------------------------------------------------
# Seasons & episodes
# ---------------------------------------------------------------------------


class Season(_CamelModel):
    """Season summary for a TV series."""

    season: str
    episode_count: int = 0


class ListTitleSeasonsResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/seasons``."""

    seasons: list[Season] = []


class Episode(_CamelModel):
    """A single TV episode."""

    id: str
    title: str | None = None
    primary_image: Image | None = None
    season: str | None = None
    episode_number: int | None = None
    runtime_seconds: int | None = None
    plot: str | None = None
    rating: Rating | None = None
    release_date: PrecisionDate | None = None


class ListTitleEpisodesResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/episodes``."""

    episodes: list[Episode] = []
    total_count: int = 0
    next_page_token: str | None = None


# ---------------------------------------------------------------------------
# Images & videos
# ---------------------------------------------------------------------------


class TitleImage(_CamelModel):
    """An image associated with a title (poster, still frame, event photo, etc.)."""

    url: str
    width: int
    height: int
    type: str | None = None


class ListTitleImagesResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/images``."""

    images: list[TitleImage] = []
    total_count: int = 0
    next_page_token: str | None = None


class Video(_CamelModel):
    """A video clip (trailer, featurette, clip, etc.)."""

    id: str
    type: str | None = None
    name: str | None = None
    primary_image: Image | None = None
    description: str | None = None
    width: int | None = None
    height: int | None = None
    runtime_seconds: int | None = None


class ListTitleVideosResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/videos``."""

    videos: list[Video] = []
    total_count: int = 0
    next_page_token: str | None = None


# ---------------------------------------------------------------------------
# Award nominations
# ---------------------------------------------------------------------------


class AwardNominationStats(_CamelModel):
    """Aggregated award statistics for a title."""

    nomination_count: int = 0
    win_count: int = 0


class AwardNomination(_CamelModel):
    """A single award nomination record."""

    titles: list[TitleRef] = []
    nominees: list[NameRef] = []
    event: Event | None = None
    year: int | None = None
    text: str | None = None
    category: str | None = None
    is_winner: bool = False
    winner_rank: int | None = None


class ListTitleAwardNominationsResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/awardNominations``."""

    stats: AwardNominationStats | None = None
    award_nominations: list[AwardNomination] = []
    next_page_token: str | None = None


# ---------------------------------------------------------------------------
# Parents guide
# ---------------------------------------------------------------------------


class SeverityBreakdown(_CamelModel):
    """Vote breakdown by severity level for a parents-guide category."""

    severity_level: str
    vote_count: int = 0


class ParentsGuideReview(_CamelModel):
    """A user-written review entry for a parents-guide category."""

    text: str
    is_spoiler: bool = False


class ParentsGuide(_CamelModel):
    """Content advisory data for one category (violence, language, etc.)."""

    category: ParentsGuideCategory | None = None
    severity_breakdowns: list[SeverityBreakdown] = []
    reviews: list[ParentsGuideReview] = []


class ListTitleParentsGuideResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/parentsGuide``."""

    parents_guide: list[ParentsGuide] = []


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------


class Certificate(_CamelModel):
    """A content rating certificate issued by a regional authority."""

    rating: str
    country: Country | None = None
    attributes: list[str] = []


class ListTitleCertificatesResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/certificates``."""

    certificates: list[Certificate] = []
    total_count: int = 0


# ---------------------------------------------------------------------------
# Company credits
# ---------------------------------------------------------------------------


class YearsInvolved(_CamelModel):
    """Year range a company was involved with a title."""

    start_year: int | None = None
    end_year: int | None = None


class CompanyCredit(_CamelModel):
    """A company's involvement in a title's production or distribution."""

    company: Company | None = None
    category: str | None = None
    countries: list[Country] = []
    years_involved: YearsInvolved | None = None
    attributes: list[str] = []


class ListTitleCompanyCreditsResponse(_CamelModel):
    """Response from ``GET /titles/{titleId}/companyCredits``."""

    company_credits: list[CompanyCredit] = []
    total_count: int = 0
    next_page_token: str | None = None


# ---------------------------------------------------------------------------
# Box office
# ---------------------------------------------------------------------------


class OpeningWeekendGross(_CamelModel):
    """Opening-weekend gross revenue."""

    gross: Money | None = None
    weekend_end_date: PrecisionDate | None = None


class BoxOffice(_CamelModel):
    """Box office financial data for a title."""

    domestic_gross: Money | None = None
    worldwide_gross: Money | None = None
    opening_weekend_gross: OpeningWeekendGross | None = None
    production_budget: Money | None = None


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class SearchTitlesResponse(_CamelModel):
    """Response from ``GET /search/titles``."""

    titles: list[Title] = []
