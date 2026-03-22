"""Titles endpoint — wraps all ``/titles`` API operations."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from ..exceptions import IMDBAPIValidationError
from ..models.title import (
    BatchGetTitlesResponse,
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
    SortBy,
    SortOrder,
    Title,
    TitleType,
)
from ..pagination import AsyncPaginator
from .base import BaseEndpoint


class TitlesEndpoint(BaseEndpoint):
    """All ``/titles`` endpoint operations.

    Instantiated automatically by :class:`~imdbapi.client.IMDBAPIClient` and
    accessible via ``client.titles``.
    """

    # ------------------------------------------------------------------
    # List / search
    # ------------------------------------------------------------------

    async def list(
        self,
        *,
        types: list[TitleType] | None = None,
        genres: list[str] | None = None,
        country_codes: list[str] | None = None,
        language_codes: list[str] | None = None,
        name_ids: list[str] | None = None,
        interest_ids: list[str] | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        min_vote_count: int | None = None,
        max_vote_count: int | None = None,
        min_aggregate_rating: float | None = None,
        max_aggregate_rating: float | None = None,
        sort_by: SortBy | None = None,
        sort_order: SortOrder | None = None,
        page_token: str | None = None,
    ) -> ListTitlesResponse:
        """Retrieve a filtered, paginated list of titles.

        Parameters
        ----------
        types:
            Filter by title type (MOVIE, TV_SERIES, …).
        genres:
            Filter by genre strings (e.g. ``["Action", "Drama"]``).
        country_codes:
            ISO 3166-1 alpha-2 country codes.
        language_codes:
            ISO 639-1/639-2 language codes.
        name_ids:
            IMDb person IDs (``nm…``) to filter by actor / creator.
        interest_ids:
            Interest / genre taxonomy IDs.
        start_year:
            Earliest release year (inclusive).
        end_year:
            Latest release year (inclusive).
        min_vote_count:
            Minimum number of IMDb votes.
        max_vote_count:
            Maximum number of IMDb votes.
        min_aggregate_rating:
            Minimum IMDb aggregate rating (0.0–10.0).
        max_aggregate_rating:
            Maximum IMDb aggregate rating (0.0–10.0).
        sort_by:
            Field to sort by.
        sort_order:
            ``ASC`` or ``DESC``.
        page_token:
            Pagination cursor from a previous response.

        Returns
        -------
        ListTitlesResponse
            Page of matching titles plus a cursor for the next page.
        """
        params: dict[str, Any] = self._clean(
            {
                "types[]": [t.value for t in types] if types else None,
                "genres[]": genres,
                "countryCodes[]": country_codes,
                "languageCodes[]": language_codes,
                "nameIds[]": name_ids,
                "interestIds[]": interest_ids,
                "startYear": start_year,
                "endYear": end_year,
                "minVoteCount": min_vote_count,
                "maxVoteCount": max_vote_count,
                "minAggregateRating": min_aggregate_rating,
                "maxAggregateRating": max_aggregate_rating,
                "sortBy": sort_by.value if sort_by else None,
                "sortOrder": sort_order.value if sort_order else None,
                "pageToken": page_token,
            }
        )
        raw = await self._get("/titles", params=params)
        try:
            return ListTitlesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    def list_pages(self, **kwargs: Any) -> AsyncPaginator[ListTitlesResponse]:
        """Return an async iterator that auto-follows pagination cursors.

        Accepts the same keyword arguments as :meth:`list`.

        Examples
        --------
        ::

            async for page in client.titles.list_pages(genres=["Action"]):
                for title in page.titles:
                    print(title.primary_title)
        """
        return AsyncPaginator(self.list, **kwargs)

    async def get(self, title_id: str) -> Title:
        """Fetch a single title by its IMDb ID.

        Parameters
        ----------
        title_id:
            IMDb title identifier (format: ``tt1234567``).

        Returns
        -------
        Title
            Full title object.

        Raises
        ------
        IMDBAPINotFoundError
            If the title ID does not exist.
        """
        raw = await self._get(f"/titles/{title_id}")
        try:
            return Title.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def batch_get(self, title_ids: list[str]) -> BatchGetTitlesResponse:
        """Fetch up to 5 titles in a single request.

        Parameters
        ----------
        title_ids:
            List of IMDb title IDs (maximum 5).

        Returns
        -------
        BatchGetTitlesResponse
            Container with the requested title objects.
        """
        raw = await self._get("/titles:batchGet", params={"titleIds[]": title_ids})
        try:
            return BatchGetTitlesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    # ------------------------------------------------------------------
    # Sub-resources
    # ------------------------------------------------------------------

    async def get_credits(
        self,
        title_id: str,
        *,
        categories: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListTitleCreditsResponse:
        """Fetch cast and crew credits for a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        categories:
            Filter by credit category strings.
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListTitleCreditsResponse
        """
        params = self._clean(
            {
                "categories[]": categories,
                "pageSize": page_size,
                "pageToken": page_token,
            }
        )
        raw = await self._get(f"/titles/{title_id}/credits", params=params)
        try:
            return ListTitleCreditsResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    def get_credits_pages(
        self, title_id: str, **kwargs: Any
    ) -> AsyncPaginator[ListTitleCreditsResponse]:
        """Auto-paginating iterator for title credits.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        **kwargs:
            Additional keyword arguments forwarded to :meth:`get_credits`.
        """
        return AsyncPaginator(lambda **kw: self.get_credits(title_id, **kw), **kwargs)

    async def get_release_dates(
        self,
        title_id: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListTitleReleaseDatesResponse:
        """Fetch regional release dates for a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListTitleReleaseDatesResponse
        """
        params = self._clean({"pageSize": page_size, "pageToken": page_token})
        raw = await self._get(f"/titles/{title_id}/releaseDates", params=params)
        try:
            return ListTitleReleaseDatesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_akas(self, title_id: str) -> ListTitleAKAsResponse:
        """Fetch alternative / localised titles (AKAs).

        Parameters
        ----------
        title_id:
            IMDb title ID.

        Returns
        -------
        ListTitleAKAsResponse
        """
        raw = await self._get(f"/titles/{title_id}/akas")
        try:
            return ListTitleAKAsResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_seasons(self, title_id: str) -> ListTitleSeasonsResponse:
        """Fetch the season list for a TV series.

        Parameters
        ----------
        title_id:
            IMDb title ID (must be a TV series).

        Returns
        -------
        ListTitleSeasonsResponse
        """
        raw = await self._get(f"/titles/{title_id}/seasons")
        try:
            return ListTitleSeasonsResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_episodes(
        self,
        title_id: str,
        *,
        season: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListTitleEpisodesResponse:
        """Fetch episodes for a TV series, optionally filtered by season.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        season:
            Season number string (e.g. ``"1"``).
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListTitleEpisodesResponse
        """
        params = self._clean(
            {"season": season, "pageSize": page_size, "pageToken": page_token}
        )
        raw = await self._get(f"/titles/{title_id}/episodes", params=params)
        try:
            return ListTitleEpisodesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    def get_episodes_pages(
        self, title_id: str, **kwargs: Any
    ) -> AsyncPaginator[ListTitleEpisodesResponse]:
        """Auto-paginating iterator for title episodes.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        **kwargs:
            Additional keyword arguments forwarded to :meth:`get_episodes`.
        """
        return AsyncPaginator(lambda **kw: self.get_episodes(title_id, **kw), **kwargs)

    async def get_images(
        self,
        title_id: str,
        *,
        types: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListTitleImagesResponse:
        """Fetch images associated with a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        types:
            Image type filters (e.g. ``["poster", "still_frame"]``).
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListTitleImagesResponse
        """
        params = self._clean(
            {"types[]": types, "pageSize": page_size, "pageToken": page_token}
        )
        raw = await self._get(f"/titles/{title_id}/images", params=params)
        try:
            return ListTitleImagesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_videos(
        self,
        title_id: str,
        *,
        types: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListTitleVideosResponse:
        """Fetch video clips associated with a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        types:
            Video type filters.
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListTitleVideosResponse
        """
        params = self._clean(
            {"types[]": types, "pageSize": page_size, "pageToken": page_token}
        )
        raw = await self._get(f"/titles/{title_id}/videos", params=params)
        try:
            return ListTitleVideosResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_award_nominations(
        self,
        title_id: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListTitleAwardNominationsResponse:
        """Fetch award nomination records for a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListTitleAwardNominationsResponse
        """
        params = self._clean({"pageSize": page_size, "pageToken": page_token})
        raw = await self._get(f"/titles/{title_id}/awardNominations", params=params)
        try:
            return ListTitleAwardNominationsResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_parents_guide(self, title_id: str) -> ListTitleParentsGuideResponse:
        """Fetch parental content advisory data for a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.

        Returns
        -------
        ListTitleParentsGuideResponse
        """
        raw = await self._get(f"/titles/{title_id}/parentsGuide")
        try:
            return ListTitleParentsGuideResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_certificates(self, title_id: str) -> ListTitleCertificatesResponse:
        """Fetch regional content-rating certificates for a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.

        Returns
        -------
        ListTitleCertificatesResponse
        """
        raw = await self._get(f"/titles/{title_id}/certificates")
        try:
            return ListTitleCertificatesResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_company_credits(
        self,
        title_id: str,
        *,
        categories: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ListTitleCompanyCreditsResponse:
        """Fetch production / distribution company credits for a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.
        categories:
            Company role filters (e.g. ``["production", "distribution"]``).
        page_size:
            Results per page (1–50, default 20).
        page_token:
            Pagination cursor.

        Returns
        -------
        ListTitleCompanyCreditsResponse
        """
        params = self._clean(
            {"categories[]": categories, "pageSize": page_size, "pageToken": page_token}
        )
        raw = await self._get(f"/titles/{title_id}/companyCredits", params=params)
        try:
            return ListTitleCompanyCreditsResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    async def get_box_office(self, title_id: str) -> BoxOffice:
        """Fetch box-office financial data for a title.

        Parameters
        ----------
        title_id:
            IMDb title ID.

        Returns
        -------
        BoxOffice
            Revenue, budget, and opening-weekend data.
        """
        raw = await self._get(f"/titles/{title_id}/boxOffice")
        try:
            return BoxOffice.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc
