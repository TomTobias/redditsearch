"""Logging configuration for the application"""
import logging
import sys
from rich.logging import RichHandler


def setup_logger(name: str = "redditsearch", level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with Rich formatting

    Args:
        name: Logger name (default: "redditsearch")
        level: Logging level (default: INFO)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logger()
        >>> logger.info("Starting search...")
        >>> logger.error("An error occurred")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Use Rich handler for beautiful console output
    handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=False,
    )

    # Format: timestamp - level - message
    formatter = logging.Formatter(
        "%(message)s",
        datefmt="[%X]",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


# Default logger instance
logger = setup_logger()
