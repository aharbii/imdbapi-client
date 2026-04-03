"""Async pagination helpers.

Usage example::

    async for page in client.titles.list_pages(genres=["Action"]):
        for title in page.titles:
            print(title.primary_title)
        if not page.next_page_token:
            break  # already handled by the iterator, but explicit is fine
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any, Protocol, TypeVar


class _PagedResponse(Protocol):
    """Structural type for any paginated API response."""

    next_page_token: str | None


PageT = TypeVar("PageT", bound=_PagedResponse)

# The fetch function accepts an optional page_token keyword argument and
# returns a coroutine that resolves to a paged response.
FetchFunc = Callable[..., Coroutine[Any, Any, PageT]]


class AsyncPaginator[PageT: _PagedResponse]:
    """Generic async iterator that follows ``nextPageToken`` cursors.

    Parameters
    ----------
    fetch_func:
        An async callable that accepts a ``page_token`` keyword argument and
        returns a response object with a ``next_page_token`` attribute.
    kwargs:
        Additional keyword arguments forwarded to ``fetch_func`` on every call
        (filters, page sizes, etc.).

    Examples
    --------
    ::

        paginator = AsyncPaginator(client.titles.list, genres=["Action"])
        async for page in paginator:
            process(page.titles)
    """

    def __init__(self, fetch_func: FetchFunc[PageT], **kwargs: Any) -> None:
        self._fetch = fetch_func
        self._kwargs = kwargs

    def __aiter__(self) -> AsyncIterator[PageT]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[PageT]:
        page_token: str | None = None
        while True:
            page: PageT = await self._fetch(page_token=page_token, **self._kwargs)
            yield page
            page_token = page.next_page_token
            if not page_token:
                break
