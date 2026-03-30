"""imdbapi-client — async Python client for imdbapi.dev.

Public API::

    from imdbapi import IMDBAPIClient
    from imdbapi.exceptions import IMDBAPINotFoundError, IMDBAPIRateLimitError
    from imdbapi.models import Title, Name, TitleType
"""

from imdbapi.client import IMDBAPIClient
from imdbapi.exceptions import (
    IMDBAPIBadRequestError,
    IMDBAPIConnectionError,
    IMDBAPIError,
    IMDBAPIHTTPError,
    IMDBAPINotFoundError,
    IMDBAPIRateLimitError,
    IMDBAPIServerError,
    IMDBAPITimeoutError,
    IMDBAPIValidationError,
)

__version__ = "0.1.0"

__all__ = [
    "IMDBAPIClient",
    # exceptions
    "IMDBAPIBadRequestError",
    "IMDBAPIConnectionError",
    "IMDBAPIError",
    "IMDBAPIHTTPError",
    "IMDBAPINotFoundError",
    "IMDBAPIRateLimitError",
    "IMDBAPIServerError",
    "IMDBAPITimeoutError",
    "IMDBAPIValidationError",
]
