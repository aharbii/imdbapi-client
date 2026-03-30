"""Search endpoint — wraps ``GET /search/titles``."""

from __future__ import annotations

from pydantic import ValidationError

from imdbapi.endpoints.base import BaseEndpoint
from imdbapi.exceptions import IMDBAPIValidationError
from imdbapi.models.title import SearchTitlesResponse


class SearchEndpoint(BaseEndpoint):
    """Full-text search operations.

    Instantiated automatically by :class:`~imdbapi.client.IMDBAPIClient` and
    accessible via ``client.search``.
    """

    async def titles(self, query: str, *, limit: int | None = None) -> SearchTitlesResponse:
        """Search IMDb titles by keyword.

        Performs a full-text search and returns up to ``limit`` matching
        titles ranked by relevance.

        Parameters
        ----------
        query:
            The search keyword or phrase.
        limit:
            Maximum number of results to return (1–50).

        Returns
        -------
        SearchTitlesResponse
            List of matching title objects.
        """
        params = self._clean({"query": query, "limit": limit})
        raw = await self._get("/search/titles", params=params)
        try:
            return SearchTitlesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc
