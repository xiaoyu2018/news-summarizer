"""Logging configuration for news-summarizer."""

import logging
import sys


def setup_logger(
    name: str = "news-summarizer",
    level: str = "INFO",
    include_instance: bool = True,
) -> logging.Logger:
    """Set up and configure logger.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        include_instance: Whether to include instance name in logs

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))

        if include_instance:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(instance)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str = "news-summarizer") -> logging.Logger:
    """Get an existing logger.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
