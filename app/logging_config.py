"""Logging configuration.

Provides structured logging setup for development and production.
"""

import logging
import sys
from typing import Optional


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure application logging.

    Sets up structured logging with appropriate formatters and handlers
    for both development and production environments.
    """
    level: int = getattr(logging, (log_level or 'INFO').upper(), logging.INFO)

    # Formatters
    detailed_format: str = (
        '[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d - %(message)s'
    )
    simple_format: str = '%(levelname)-8s %(message)s'
    console_format: str = '%(levelname)-8s %(name)s - %(message)s'

    # Handlers
    handlers: list[logging.Handler] = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(console_format))
    handlers.append(console_handler)

    # File handler (only in production)
    if level > logging.DEBUG:
        file_handler = logging.FileHandler('app.log', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(detailed_format))
        handlers.append(file_handler)

    # Root Logger Configuration
    logging.basicConfig(
        level=level,
        format=detailed_format,
        handlers=handlers,
        force=True,
    )

    # Reduce noise from third-party libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(name)
