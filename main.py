"""Entry-point demonstrating basic usage of the imdbapi client.

Run from an attached container session or `make shell`, then::

    python main.py
"""

from __future__ import annotations

import asyncio

from imdbapi import IMDBAPIClient
from imdbapi.exceptions import IMDBAPIError
from imdbapi.models import TitleType
from imdbapi.utils.logger import get_logger

logger = get_logger(__name__)


async def main() -> None:
    """Demonstrate searching and fetching titles and persons."""
    async with IMDBAPIClient(debug=True) as client:
        # ----------------------------------------------------------------
        # Search for a title
        # ----------------------------------------------------------------
        logger.info("Searching for 'The Shawshank Redemption' …")
        search_result = await client.search.titles("The Shawshank Redemption", limit=1)
        if not search_result.titles:
            logger.warning("No results found.")
            return

        title = search_result.titles[0]
        logger.info("Found: %s (%s) — id=%s", title.primary_title, title.start_year, title.id)

        # ----------------------------------------------------------------
        # Fetch the full title record
        # ----------------------------------------------------------------
        full_title = await client.titles.get(title.id)
        logger.info(
            "Rating: %.1f / 10  (%s votes)",
            full_title.rating.aggregate_rating if full_title.rating else 0.0,
            f"{full_title.rating.vote_count:,}" if full_title.rating else "—",
        )

        # ----------------------------------------------------------------
        # List top-rated movies (first page)
        # ----------------------------------------------------------------
        logger.info("Fetching top-rated movies …")
        movies = await client.titles.list(
            types=[TitleType.MOVIE],
            min_aggregate_rating=8.0,
            min_vote_count=100_000,
        )
        logger.info("Total matching: %d  (showing %d)", movies.total_count, len(movies.titles))
        for t in movies.titles[:5]:
            logger.info(
                "  • %s (%s) — %.1f",
                t.primary_title,
                t.start_year,
                t.rating.aggregate_rating if t.rating else 0.0,
            )

        # ----------------------------------------------------------------
        # Fetch a person
        # ----------------------------------------------------------------
        if full_title.directors:
            director_ref = full_title.directors[0]
            logger.info("Fetching director: %s (%s)", director_ref.display_name, director_ref.id)
            director = await client.names.get(director_ref.id)
            logger.info(
                "Bio snippet: %s",
                (director.biography or "")[:120].replace("\n", " "),
            )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except IMDBAPIError as exc:
        logger.error("API error: %s", exc)
        raise SystemExit(1) from exc
