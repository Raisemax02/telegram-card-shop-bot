"""
Logging configuration — Centralized logging setup.

Provides console and rotating file handlers with structured formatting.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_configured = False


def setup_logging(log_level: int | None = None) -> None:
    """Configure application-wide logging with console and file output.

    Uses a rotating file handler (5 MB max, 3 backups) alongside
    a console handler. Suppresses noisy third-party loggers.
    Calling this function more than once is a no-op.

    Log level can be set via the LOG_LEVEL environment variable
    (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.
    """
    global _configured  # noqa: PLW0603
    if _configured:
        return
    _configured = True

    if log_level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, env_level, logging.INFO)

    # Navigate from app/bot/logger.py -> app/bot/ -> app/ -> root/
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Rotating file handler (5 MB, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_dir / "bot.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Root logger
    root = logging.getLogger()
    root.setLevel(log_level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
