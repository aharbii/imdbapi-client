"""Charts endpoint — wraps ``GET /chart/starmeter``."""

from __future__ import annotations

from pydantic import ValidationError

from ..exceptions import IMDBAPIValidationError
from ..models.name import ListStarMetersResponse
from ..pagination import AsyncPaginator
from .base import BaseEndpoint


class ChartsEndpoint(BaseEndpoint):
    """IMDb chart operations.

    Instantiated automatically by :class:`~imdbapi.client.IMDBAPIClient` and
    accessible via ``client.charts``.
    """

    async def starmeter(self, *, page_token: str | None = None) -> ListStarMetersResponse:
        """Fetch the current IMDb StarMeter popularity rankings.

        The StarMeter ranks people by their current popularity on IMDb.
        Results are paginated.

        Parameters
        ----------
        page_token:
            Pagination cursor from a previous response.

        Returns
        -------
        ListStarMetersResponse
            Ranked list of persons with meter ranking data.
        """
        params = self._clean({"pageToken": page_token})
        raw = await self._get("/chart/starmeter", params=params)
        try:
            return ListStarMetersResponse.model_validate(raw)
        except ValidationError as exc:
            raise IMDBAPIValidationError(str(exc), raw=raw) from exc

    def starmeter_pages(self) -> AsyncPaginator[ListStarMetersResponse]:
        """Auto-paginating iterator for the full StarMeter chart.

        Examples
        --------
        ::

            async for page in client.charts.starmeter_pages():
                for person in page.names:
                    print(person.display_name, person.meter_ranking)
        """
        return AsyncPaginator(self.starmeter)
