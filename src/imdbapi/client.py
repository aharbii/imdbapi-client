"""Core HTTP client for the imdbapi.dev REST API.

The :class:`IMDBAPIClient` is the single entry-point for all API operations.
It wraps an ``httpx.AsyncClient``, applies a tenacity retry policy for
transient errors, maps HTTP status codes to typed exceptions, and exposes
five endpoint groups as attributes.

Usage
-----
Async context-manager (recommended)::

    async with IMDBAPIClient() as client:
        title = await client.titles.get("tt0111161")
        print(title.primary_title)

Manual lifecycle::

    client = IMDBAPIClient()
    await client.open()
    try:
        title = await client.titles.get("tt0111161")
    finally:
        await client.close()

Sync convenience (wraps asyncio.run)::

    import asyncio
    title = asyncio.run(client.titles.get("tt0111161"))
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from imdbapi.endpoints.charts import ChartsEndpoint
from imdbapi.endpoints.interests import InterestsEndpoint
from imdbapi.endpoints.names import NamesEndpoint
from imdbapi.endpoints.search import SearchEndpoint
from imdbapi.endpoints.titles import TitlesEndpoint
from imdbapi.exceptions import (
    IMDBAPIBadRequestError,
    IMDBAPIConnectionError,
    IMDBAPIError,
    IMDBAPIHTTPError,
    IMDBAPINotFoundError,
    IMDBAPIRateLimitError,
    IMDBAPIServerError,
    IMDBAPITimeoutError,
)
from imdbapi.utils.logger import get_logger

_RETRYABLE = (IMDBAPIServerError, IMDBAPIConnectionError, IMDBAPITimeoutError)

_DEFAULT_BASE_URL = "https://api.imdbapi.dev"
_DEFAULT_TIMEOUT = 30.0
_DEFAULT_MAX_RETRIES = 3


class IMDBAPIClient:
    """Async HTTP client for the imdbapi.dev REST API (v2.7.12).

    Parameters
    ----------
    base_url:
        Override the API base URL (useful for integration tests with a mock
        server).  Defaults to ``https://api.imdbapi.dev``.
    timeout:
        Total request timeout in seconds.  Defaults to 30.
    max_retries:
        Number of retry attempts for transient errors (server errors, timeouts,
        connection failures).  Set to ``1`` to disable retries.  Defaults to 3.
    api_key:
        Optional API key sent as the ``X-API-Key`` header.  The public API
        does not currently require authentication, but the parameter is
        provided for forward-compatibility.
    debug:
        Enable ``DEBUG``-level logging for requests and responses.
    """

    def __init__(
        self,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        api_key: str | None = None,
        debug: bool = False,
    ) -> None:
        self.debug = debug
        self._max_retries = max_retries
        self._logger = get_logger(__name__)

        headers: dict[str, str] = {"Accept": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key

        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

        # Endpoint groups — instantiated once and reused
        self.titles = TitlesEndpoint(self)
        self.names = NamesEndpoint(self)
        self.interests = InterestsEndpoint(self)
        self.search = SearchEndpoint(self)
        self.charts = ChartsEndpoint(self)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def open(self) -> None:
        """Explicitly open the underlying HTTP connection pool.

        Prefer the async context-manager interface (``async with``) over
        calling this method directly.
        """
        # httpx.AsyncClient is ready on construction; this is a no-op kept
        # for API symmetry with ``close``.
        self._logger.debug(f"IMDBAPIClient opened (base_url={self._http.base_url})")

    async def close(self) -> None:
        """Close the underlying HTTP connection pool and release resources."""
        await self._http.aclose()
        self._logger.debug("IMDBAPIClient closed")

    async def __aenter__(self) -> IMDBAPIClient:
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Internal HTTP layer
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an HTTP request with retry and error mapping.

        Transient failures (5xx, timeouts, connection errors) are retried up
        to ``max_retries`` times with exponential back-off.  Client errors
        (4xx) are not retried.

        Parameters
        ----------
        method:
            HTTP verb (``"GET"``, ``"POST"``, …).
        path:
            URL path relative to the configured base URL.
        params:
            Query parameters.

        Returns
        -------
        dict[str, Any]
            Parsed JSON response body.

        Raises
        ------
        IMDBAPIBadRequestError
            On HTTP 400.
        IMDBAPINotFoundError
            On HTTP 404.
        IMDBAPIRateLimitError
            On HTTP 429.
        IMDBAPIServerError
            On HTTP 5xx (after exhausting retries).
        IMDBAPIConnectionError
            On DNS / connect failures (after exhausting retries).
        IMDBAPITimeoutError
            On request timeout (after exhausting retries).
        """
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(_RETRYABLE),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            before_sleep=before_sleep_log(self._logger, logging.WARNING),
            reraise=True,
        ):
            with attempt:
                return await self._execute(method, path, params=params)

        # Unreachable — tenacity reraises on exhaustion with reraise=True
        raise IMDBAPIError("Retry loop exited without result")  # pragma: no cover

    async def _execute(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a single HTTP request without retry logic.

        Parameters
        ----------
        method:
            HTTP verb.
        path:
            URL path.
        params:
            Query parameters.

        Returns
        -------
        dict[str, Any]
            Parsed JSON body on success.

        Raises
        ------
        IMDBAPITimeoutError
            On ``httpx.TimeoutException``.
        IMDBAPIConnectionError
            On ``httpx.ConnectError`` or other ``httpx.HTTPError``.
        IMDBAPIHTTPError
            Subclass matching the HTTP status code.
        """
        self._logger.debug(f"→ {method} {path} params={params}")
        try:
            response = await self._http.request(method, path, params=params)
        except httpx.TimeoutException as exc:
            raise IMDBAPITimeoutError(f"Request timed out: {method} {path}") from exc
        except httpx.ConnectError as exc:
            raise IMDBAPIConnectionError(f"Connection error: {method} {path} — {exc}") from exc
        except httpx.HTTPError as exc:
            raise IMDBAPIConnectionError(f"HTTP transport error: {method} {path} — {exc}") from exc

        self._logger.debug(
            f"← {method} {path} → HTTP {response.status_code} ({len(response.content)} bytes)"
        )

        if response.is_success:
            data: dict[str, Any] = response.json()
            return data

        # Parse the error body produced by the API
        message, details = self._parse_error_body(response)

        status = response.status_code
        if status == 400:
            raise IMDBAPIBadRequestError(status, message, details)
        if status == 404:
            raise IMDBAPINotFoundError(status, message, details)
        if status == 429:
            raise IMDBAPIRateLimitError(status, message, details)
        if status >= 500:
            raise IMDBAPIServerError(status, message, details)
        raise IMDBAPIHTTPError(status, message, details)

    @staticmethod
    def _parse_error_body(
        response: httpx.Response,
    ) -> tuple[str, list[dict[str, object]]]:
        """Extract ``message`` and ``details`` from an API error response.

        Parameters
        ----------
        response:
            The failed HTTP response.

        Returns
        -------
        tuple[str, list[dict[str, object]]]
            A ``(message, details)`` tuple.  Falls back to the raw response
            text when the body is not valid JSON.
        """
        try:
            body: dict[str, Any] = response.json()
            message: str = body.get("message", response.text)
            details: list[dict[str, object]] = body.get("details", [])
            return message, details
        except Exception:
            return response.text, []
