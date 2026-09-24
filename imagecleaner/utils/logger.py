"""
ImageCleaner Logging Utilities.

This module provides the centralized logging configuration used
throughout the ImageCleaner library.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from imagecleaner.config.constants import LOG_DIRECTORY, LOG_FILE_NAME

LOGGER_NAME = "imagecleaner"

DEFAULT_LOG_LEVEL = logging.INFO

MAX_LOG_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

BACKUP_LOG_COUNT = 3

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s | %(module)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _create_log_directory(log_directory: Path) -> Path:
    """
    Create the log directory if it does not already exist.

    Args:
        log_directory: Directory where log files should be stored.

    Returns:
        The normalized log directory path.
    """
    directory = Path(log_directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _create_formatter() -> logging.Formatter:
    """
    Create the standard ImageCleaner log formatter.

    Returns:
        Configured logging formatter.
    """
    return logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )


def get_logger(
    name: str | None = None,
    *,
    level: int = DEFAULT_LOG_LEVEL,
    log_directory: Path = LOG_DIRECTORY,
) -> logging.Logger:
    """
    Return a configured ImageCleaner logger.

    The logger writes messages to both the console and a rotating
    log file.

    Args:
        name: Optional logger name. If omitted, the root
            ImageCleaner logger is returned.
        level: Logging level for the logger.
        log_directory: Directory where the log file is stored.

    Returns:
        Configured logging.Logger instance.

    Raises:
        ValueError: If the supplied logger name is empty.
    """
    if name is not None and not name.strip():
        raise ValueError("Logger name must not be empty.")

    logger_name = LOGGER_NAME if name is None else f"{LOGGER_NAME}.{name}"

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Prevent messages from being duplicated by parent loggers.
    logger.propagate = False

    # Avoid adding handlers every time get_logger() is called.
    if logger.handlers:
        return logger

    formatter = _create_formatter()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    directory = _create_log_directory(log_directory)
    log_file = directory / LOG_FILE_NAME

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=MAX_LOG_FILE_SIZE,
        backupCount=BACKUP_LOG_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def set_logger_level(logger: logging.Logger, level: int) -> None:
    """
    Change the logging level of an existing logger.

    Args:
        logger: Logger whose level should be changed.
        level: New logging level.
    """
    logger.setLevel(level)

    for handler in logger.handlers:
        handler.setLevel(level)