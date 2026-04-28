"""Logging utilities for the imdbapi package.

Library code never configures the logging system — it only obtains loggers.
Configuration is the responsibility of the entry point that imports this package.

Log level is controlled by the ``LOG_LEVEL`` environment variable set at the
entry-point level.
"""

from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a stdlib logger for the given name.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        A ``logging.Logger`` instance.
    """
    return logging.getLogger(name)
