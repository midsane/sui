import logging


def get_logger(
    name: str,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Return a configured logger.

    Example:
        logger = get_logger(__name__)
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger
