"""Logging utilities for the imdbapi package.

Library code never configures the logging system — it only obtains loggers.
Configuration is the responsibility of the entry point that imports this package.

``get_logger`` is a thin backward-compatible shim with an ignored ``debug``
parameter.  Log level is controlled by the ``LOG_LEVEL`` environment variable
set at the entry-point level.
"""

from __future__ import annotations

import logging


def get_logger(name: str, debug: bool = False) -> logging.Logger:  # noqa: ARG001
    """Return a stdlib logger for the given name.

    The ``debug`` parameter is accepted for backward compatibility but is
    ignored — log level is controlled by the entry-point bootstrap via the
    ``LOG_LEVEL`` environment variable.

    Args:
        name: Logger name, typically ``__name__``.
        debug: Ignored. Kept for backward compatibility.

    Returns:
        A ``logging.Logger`` instance.
    """
    return logging.getLogger(name)
