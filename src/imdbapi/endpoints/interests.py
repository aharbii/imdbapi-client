"""Interests endpoint — wraps all ``/interests`` API operations."""

from __future__ import annotations

from pydantic import ValidationError

from ..exceptions import IMDBAPIValidationError
from ..models.interest import Interest, ListInterestCategoriesResponse
from .base import BaseEndpoint


class InterestsEndpoint(BaseEndpoint):
    """All ``/interests`` endpoint operations.

    Instantiated automatically by :class:`~imdbapi.client.IMDBAPIClient` and
    accessible via ``client.interests``.
    """

    async def list_categories(self) -> ListInterestCategoriesResponse:
        """Fetch all interest categories (genre taxonomy).

        Returns
        -------
        ListInterestCategoriesResponse
            All top-level categories with their nested interests.
        """
        raw = await self._get("/interests")
        try:
            return ListInterestCategoriesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get(self, interest_id: str) -> Interest:
        """Fetch a single interest / genre by its ID.

        Parameters
        ----------
        interest_id:
            IMDb interest identifier.

        Returns
        -------
        Interest
            Full interest object including description and similar interests.

        Raises
        ------
        IMDBAPINotFoundError
            If the interest ID does not exist.
        """
        raw = await self._get(f"/interests/{interest_id}")
        try:
            return Interest.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc
