"""Configured application logger."""

import logging
from typing import TYPE_CHECKING

from loguru import logger as _logger

from app.settings import settings

if TYPE_CHECKING:  # To avoid circular import
    from loguru import Logger


# This code copied from loguru docs, ignoring all linters warnings
# https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record):  # type: ignore
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS352, WPS609
            frame = frame.f_back  # type: ignore [assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger() -> "Logger":
    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    return _logger


logger = setup_logger()
