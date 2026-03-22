"""Names endpoint — wraps all ``/names`` API operations."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from ..exceptions import IMDBAPIValidationError
from ..models.name import (
    BatchGetNamesResponse,
    ListNameFilmographyResponse,
    ListNameImagesResponse,
    ListNameRelationshipsResponse,
    ListNameTriviaResponse,
    Name,
)
from ..pagination import AsyncPaginator
from .base import BaseEndpoint


class NamesEndpoint(BaseEndpoint):
    """All ``/names`` endpoint operations.

    Instantiated automatically by :class:`~imdbapi.client.IMDBAPIClient` and
    accessible via ``client.names``.
    """

    async def get(self, name_id: str) -> Name:
        """Fetch a single person by their IMDb ID.

        Parameters
        ----------
        name_id:
            IMDb person identifier (format: ``nm1234567``).

        Returns
        -------
        Name
            Full person object including biography, birth info, and rankings.

        Raises
        ------
        IMDBAPINotFoundError
            If the name ID does not exist.
        """
        raw = await self._get(f"/names/{name_id}")
        try:
            return Name.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def batch_get(self, name_ids: list[str]) -> BatchGetNamesResponse:
        """Fetch up to 5 persons in a single request.

        Parameters
        ----------
        name_ids:
            List of IMDb person IDs (maximum 5).

        Returns
        -------
        BatchGetNamesResponse
            Container with the requested person objects.
        """
        raw = await self._get("/names:batchGet", params={"nameIds[]": name_ids})
        try:
            return BatchGetNamesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_images(
        self,
        name_id: str,
        *,
        types: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListNameImagesResponse:
        """Fetch images for a person.

        Parameters
        ----------
        name_id:
            IMDb person ID.
        types:
            Image type filters.
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListNameImagesResponse
        """
        params = self._clean(
            {"types[]": types, "pageSize": page_size, "pageToken": page_token}
        )
        raw = await self._get(f"/names/{name_id}/images", params=params)
        try:
            return ListNameImagesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_filmography(
        self,
        name_id: str,
        *,
        categories: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListNameFilmographyResponse:
        """Fetch the filmography (credits) for a person.

        Parameters
        ----------
        name_id:
            IMDb person ID.
        categories:
            Role type filters (e.g. ``["actor", "director"]``).
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListNameFilmographyResponse
        """
        params = self._clean(
            {"categories[]": categories, "pageSize": page_size, "pageToken": page_token}
        )
        raw = await self._get(f"/names/{name_id}/filmography", params=params)
        try:
            return ListNameFilmographyResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    def get_filmography_pages(
        self, name_id: str, **kwargs: Any
    ) -> AsyncPaginator[ListNameFilmographyResponse]:
        """Auto-paginating iterator for a person's filmography.

        Parameters
        ----------
        name_id:
            IMDb person ID.
        **kwargs:
            Additional keyword arguments forwarded to :meth:`get_filmography`.
        """
        return AsyncPaginator(lambda **kw: self.get_filmography(name_id, **kw), **kwargs)

    async def get_relationships(self, name_id: str) -> ListNameRelationshipsResponse:
        """Fetch personal / professional relationships for a person.

        Parameters
        ----------
        name_id:
            IMDb person ID.

        Returns
        -------
        ListNameRelationshipsResponse
        """
        raw = await self._get(f"/names/{name_id}/relationships")
        try:
            return ListNameRelationshipsResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_trivia(
        self,
        name_id: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListNameTriviaResponse:
        """Fetch trivia entries for a person.

        Parameters
        ----------
        name_id:
            IMDb person ID.
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListNameTriviaResponse
        """
        params = self._clean({"pageSize": page_size, "pageToken": page_token})
        raw = await self._get(f"/names/{name_id}/trivia", params=params)
        try:
            return ListNameTriviaResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc
