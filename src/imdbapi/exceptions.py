"""Custom exceptions for the IMDB API client.

Hierarchy
---------
IMDBAPIError
├── IMDBAPIHTTPError          # HTTP-level errors from the remote API
│   ├── IMDBAPIBadRequestError   # 400
│   ├── IMDBAPINotFoundError     # 404
│   ├── IMDBAPIRateLimitError    # 429
│   └── IMDBAPIServerError       # 5xx  (retryable)
├── IMDBAPIConnectionError       # Network / DNS failures  (retryable)
├── IMDBAPITimeoutError          # Request timeout         (retryable)
└── IMDBAPIValidationError       # Response schema mismatch
"""

from __future__ import annotations


class IMDBAPIError(Exception):
    """Base exception for all IMDB API client errors."""


class IMDBAPIHTTPError(IMDBAPIError):
    """HTTP-level error returned by the remote API.

    Attributes
    ----------
    status_code:
        HTTP status code from the response.
    message:
        Human-readable error description from the API.
    details:
        Optional list of structured error detail objects returned by the API.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        details: list[dict[str, object]] | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.details: list[dict[str, object]] = details or []
        super().__init__(f"HTTP {status_code}: {message}")


class IMDBAPIBadRequestError(IMDBAPIHTTPError):
    """400 Bad Request — invalid or missing request parameters."""


class IMDBAPINotFoundError(IMDBAPIHTTPError):
    """404 Not Found — the requested resource does not exist."""


class IMDBAPIRateLimitError(IMDBAPIHTTPError):
    """429 Too Many Requests — API rate limit exceeded.

    Back off and retry after a delay.
    """


class IMDBAPIServerError(IMDBAPIHTTPError):
    """5xx Server Error — transient failure on the API side.

    This error is considered retryable by the client's retry policy.
    """


class IMDBAPIConnectionError(IMDBAPIError):
    """Network connectivity error (DNS failure, connection refused, etc.).

    This error is considered retryable by the client's retry policy.
    """


class IMDBAPITimeoutError(IMDBAPIError):
    """Request timed out before a response was received.

    This error is considered retryable by the client's retry policy.
    """


class IMDBAPIValidationError(IMDBAPIError):
    """Response payload did not match the expected Pydantic schema.

    Attributes
    ----------
    raw:
        The raw payload that failed validation (for debugging).
    """

    def __init__(self, message: str, raw: object = None) -> None:
        self.raw = raw
        super().__init__(message)
