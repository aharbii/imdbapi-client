"""Shared data models used across multiple endpoint responses.

All models inherit from ``_CamelModel`` which transparently maps the API's
camelCase JSON keys to Pythonic snake_case attribute names via Pydantic's
``alias_generator``.  Unknown fields are silently ignored so the client
remains forward-compatible with new API fields.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    """Base model: accepts camelCase JSON keys, exposes snake_case attributes."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


# ---------------------------------------------------------------------------
# Primitive / reusable value types
# ---------------------------------------------------------------------------


class Image(_CamelModel):
    """Poster, thumbnail, or profile photograph."""

    url: str
    width: int
    height: int


class Country(_CamelModel):
    """ISO 3166-1 alpha-2 country representation."""

    code: str
    name: str


class Language(_CamelModel):
    """ISO 639-3 language representation."""

    code: str
    name: str


class Rating(_CamelModel):
    """Aggregate IMDb user rating."""

    aggregate_rating: float
    vote_count: int


class Metacritic(_CamelModel):
    """Metacritic critic score data."""

    url: str | None = None
    score: int
    review_count: int


class PrecisionDate(_CamelModel):
    """Partial date where any component may be absent."""

    year: int | None = None
    month: int | None = None
    day: int | None = None


class Money(_CamelModel):
    """Monetary amount with currency code."""

    amount: int
    currency: str


# ---------------------------------------------------------------------------
# Entity references used inside other resource objects
# ---------------------------------------------------------------------------


class NameRef(_CamelModel):
    """Abbreviated person reference returned inside titles and credits."""

    id: str
    display_name: str
    primary_image: Image | None = None


class Company(_CamelModel):
    """Production / distribution company reference."""

    id: str
    name: str


class Event(_CamelModel):
    """Award ceremony or event reference."""

    id: str
    name: str
