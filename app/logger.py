"""
logger.py — Application-wide structured logging configuration.

Produces JSON-friendly log lines in production (debug=False) and
human-readable coloured output during local development (debug=True).

Usage:
    from app.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Model loaded", extra={"model_path": str(path)})
"""

import logging
import sys
from typing import Optional

from app.config import settings


# ---------------------------------------------------------------------------
# Log format strings
# ---------------------------------------------------------------------------
_DEV_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)
_PROD_FORMAT = (
    '{"time":"%(asctime)s","level":"%(levelname)s",'
    '"logger":"%(name)s","line":%(lineno)d,"message":"%(message)s"}'
)


def _build_handler() -> logging.StreamHandler:
    """Return a stdout StreamHandler with the correct formatter."""
    handler = logging.StreamHandler(sys.stdout)
    fmt = _DEV_FORMAT if settings.debug else _PROD_FORMAT
    handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S"))
    return handler


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a named logger that writes to stdout.

    Calling this function multiple times with the same `name` always
    returns the same logger instance (Python's logging module caches them).
    """
    logger = logging.getLogger(name or "churn_api")
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Avoid adding duplicate handlers on repeated calls
    if not logger.handlers:
        logger.addHandler(_build_handler())
        logger.propagate = False  # don't bubble up to the root logger

    return logger
