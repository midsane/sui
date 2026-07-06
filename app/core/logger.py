"""Logging configuration."""

import logging
from pathlib import Path

# ANSI Colors
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[1;31m",  # Bold Red
}
RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    def format(self, record):  # type: ignore
        levelname = record.levelname
        color = COLORS.get(levelname, "")
        record.levelname = f"{color}{levelname:<8}{RESET}"
        return super().format(record)


def get_logger(
    create_log_file: bool = False,
    name: str = "app",
    level: int = logging.INFO,
    log_file: str = "logs/app.log",
) -> logging.Logger:
    """
    Returns a configured logger.

    Usage:
        logger = get_logger(__name__)
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Create log directory
    if create_log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)

    console_formatter = ColoredFormatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    console.setFormatter(console_formatter)

    # File handler
    file = logging.FileHandler(log_file, encoding="utf-8")
    file.setLevel(level)

    file_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file.setFormatter(file_formatter)

    logger.addHandler(console)
    logger.addHandler(file)

    logger.propagate = False

    return logger
