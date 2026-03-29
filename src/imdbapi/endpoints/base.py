"""Base endpoint class shared by all resource groups."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from imdbapi.utils.logger import get_logger

if TYPE_CHECKING:
    from imdbapi.client import IMDBAPIClient


class BaseEndpoint:
    """Provides a typed ``_get`` helper that delegates to the central client.

    Every concrete endpoint class (``TitlesEndpoint``, ``NamesEndpoint``, …)
    inherits from this class and uses ``_get`` to issue HTTP GET requests.
    The client handles retry, error mapping, and response logging.
    """

    def __init__(self, client: IMDBAPIClient) -> None:
        self._client = client
        self._logger = get_logger(__name__, debug=client.debug)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform a GET request via the parent client.

        Parameters
        ----------
        path:
            URL path relative to the configured base URL.
        params:
            Optional query parameters.  ``None`` values are automatically
            filtered out by the client before the request is sent.

        Returns
        -------
        dict[str, Any]
            Parsed JSON response body.
        """
        self._logger.debug(f"Endpoint GET {path} params={params}")
        return await self._client._request("GET", path, params=params)

    @staticmethod
    def _clean(params: dict[str, Any]) -> dict[str, Any]:
        """Remove ``None`` values from a parameter dict.

        Parameters
        ----------
        params:
            Raw parameter dict potentially containing ``None`` values.

        Returns
        -------
        dict[str, Any]
            A new dict with all ``None`` entries removed.
        """
        return {k: v for k, v in params.items() if v is not None}

    @staticmethod
    def _log_level(debug: bool) -> int:
        """Return the appropriate logging level integer.

        Parameters
        ----------
        debug:
            When ``True`` returns ``logging.DEBUG``, otherwise ``logging.INFO``.

        Returns
        -------
        int
            A ``logging`` level constant.
        """
        return logging.DEBUG if debug else logging.INFO
