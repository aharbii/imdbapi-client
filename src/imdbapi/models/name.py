"""Name (person / celebrity) data models.

Covers all response schemas from the ``/names`` and ``/chart/starmeter``
endpoint families defined in imdbapi.dev v2.7.12.
"""

from __future__ import annotations

from .common import Image, PrecisionDate, _CamelModel
from .title import Credit

# ---------------------------------------------------------------------------
# Core person object
# ---------------------------------------------------------------------------


class NameMeterRanking(_CamelModel):
    """IMDb StarMeter popularity ranking for a person."""

    current_rank: int | None = None
    change_direction: str | None = None
    difference: int | None = None


class Name(_CamelModel):
    """Full person object returned by ``GET /names/{nameId}``."""

    id: str
    display_name: str
    alternative_names: list[str] = []
    primary_image: Image | None = None
    primary_professions: list[str] = []
    biography: str | None = None
    height_cm: int | None = None
    birth_name: str | None = None
    birth_date: PrecisionDate | None = None
    birth_location: str | None = None
    death_date: PrecisionDate | None = None
    death_location: str | None = None
    death_reason: str | None = None
    meter_ranking: NameMeterRanking | None = None


# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------


class NameRelationship(_CamelModel):
    """A personal / professional relationship between two people."""

    # The API returns a full Name object; we embed it directly since Name is
    # defined above in the same module.
    name: Name | None = None
    relation_type: str | None = None
    attributes: list[str] = []


# ---------------------------------------------------------------------------
# Trivia
# ---------------------------------------------------------------------------


class NameTrivia(_CamelModel):
    """A single trivia entry for a person."""

    id: str | None = None
    text: str
    interest_count: int = 0
    vote_count: int = 0


# ---------------------------------------------------------------------------
# Paginated list responses
# ---------------------------------------------------------------------------


class ListNameImagesResponse(_CamelModel):
    """Response from ``GET /names/{nameId}/images``."""

    images: list[Image] = []
    total_count: int = 0
    next_page_token: str | None = None


class ListNameFilmographyResponse(_CamelModel):
    """Response from ``GET /names/{nameId}/filmography``."""

    credits: list[Credit] = []
    total_count: int = 0
    next_page_token: str | None = None


class ListNameRelationshipsResponse(_CamelModel):
    """Response from ``GET /names/{nameId}/relationships``."""

    relationships: list[NameRelationship] = []


class ListNameTriviaResponse(_CamelModel):
    """Response from ``GET /names/{nameId}/trivia``."""

    trivia_entries: list[NameTrivia] = []
    total_count: int = 0
    next_page_token: str | None = None


class BatchGetNamesResponse(_CamelModel):
    """Response from ``GET /names:batchGet``."""

    names: list[Name] = []


class ListStarMetersResponse(_CamelModel):
    """Response from ``GET /chart/starmeter``."""

    names: list[Name] = []
    next_page_token: str | None = None
