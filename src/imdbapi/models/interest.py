"""Interest / genre data models.

Interests are IMDb's taxonomy of genres, themes, and subgenres.  They are
returned both as lightweight references embedded in ``Title`` objects and as
full objects from the ``/interests`` endpoints.
"""

from __future__ import annotations

from .common import Image, _CamelModel


class InterestRef(_CamelModel):
    """Lightweight interest reference embedded in title responses."""

    id: str
    name: str


class Interest(_CamelModel):
    """Full interest / genre object returned by the interests endpoints."""

    id: str
    name: str
    primary_image: Image | None = None
    description: str | None = None
    is_subgenre: bool = False
    similar_interests: list[InterestRef] = []


class InterestCategory(_CamelModel):
    """A top-level category grouping related interests."""

    category: str
    interests: list[InterestRef] = []


class ListInterestCategoriesResponse(_CamelModel):
    """Response from ``GET /interests``."""

    categories: list[InterestCategory] = []
