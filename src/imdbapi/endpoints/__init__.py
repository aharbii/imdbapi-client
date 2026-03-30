"""Endpoint sub-package — one module per resource group."""

from imdbapi.endpoints.charts import ChartsEndpoint
from imdbapi.endpoints.interests import InterestsEndpoint
from imdbapi.endpoints.names import NamesEndpoint
from imdbapi.endpoints.search import SearchEndpoint
from imdbapi.endpoints.titles import TitlesEndpoint

__all__ = [
    "ChartsEndpoint",
    "InterestsEndpoint",
    "NamesEndpoint",
    "SearchEndpoint",
    "TitlesEndpoint",
]
