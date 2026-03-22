"""Tests for IMDBAPIClient lifecycle, retry logic, and error mapping."""

from __future__ import annotations

import httpx
import pytest
import respx

from imdbapi.client import IMDBAPIClient
from imdbapi.exceptions import (
    IMDBAPIBadRequestError,
    IMDBAPIConnectionError,
    IMDBAPINotFoundError,
    IMDBAPIRateLimitError,
    IMDBAPIServerError,
    IMDBAPITimeoutError,
)

BASE_URL = "https://api.imdbapi.dev"


@pytest.fixture
def client() -> IMDBAPIClient:
    return IMDBAPIClient(base_url=BASE_URL, max_retries=2, timeout=5.0)


# ---------------------------------------------------------------------------
# Context-manager lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_context_manager() -> None:
    async with IMDBAPIClient(base_url=BASE_URL) as c:
        assert c._http is not None


# ---------------------------------------------------------------------------
# HTTP error mapping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_404_raises_not_found(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt9999999").mock(
            return_value=httpx.Response(404, json={"message": "not found", "details": []})
        )
        with pytest.raises(IMDBAPINotFoundError) as exc_info:
            await client._request("GET", "/titles/tt9999999")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_400_raises_bad_request(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(
            return_value=httpx.Response(400, json={"message": "invalid param"})
        )
        with pytest.raises(IMDBAPIBadRequestError):
            await client._request("GET", "/titles")


@pytest.mark.asyncio
async def test_429_raises_rate_limit(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(return_value=httpx.Response(429, json={"message": "rate limited"}))
        with pytest.raises(IMDBAPIRateLimitError):
            await client._request("GET", "/titles")


@pytest.mark.asyncio
async def test_500_raises_server_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles").mock(
            return_value=httpx.Response(500, json={"message": "internal error"})
        )
        with pytest.raises(IMDBAPIServerError):
            await client._request("GET", "/titles")


# ---------------------------------------------------------------------------
# Network-level errors
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_timeout_raises_timeout_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt0111161").mock(side_effect=httpx.TimeoutException("timed out"))
        with pytest.raises(IMDBAPITimeoutError):
            await client._request("GET", "/titles/tt0111161")


@pytest.mark.asyncio
async def test_connect_error_raises_connection_error(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt0111161").mock(side_effect=httpx.ConnectError("connection refused"))
        with pytest.raises(IMDBAPIConnectionError):
            await client._request("GET", "/titles/tt0111161")


# ---------------------------------------------------------------------------
# Error body without JSON
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_json_error_body(client: IMDBAPIClient) -> None:
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/bad").mock(return_value=httpx.Response(500, content=b"plain text error"))
        with pytest.raises(IMDBAPIServerError) as exc_info:
            await client._request("GET", "/titles/bad")
    assert "plain text error" in exc_info.value.message


# ---------------------------------------------------------------------------
# Successful response returns parsed JSON
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_successful_response_returns_dict(client: IMDBAPIClient) -> None:
    payload = {"id": "tt0111161", "primaryTitle": "The Shawshank Redemption"}
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/titles/tt0111161").mock(return_value=httpx.Response(200, json=payload))
        result = await client._request("GET", "/titles/tt0111161")
    assert result["id"] == "tt0111161"
