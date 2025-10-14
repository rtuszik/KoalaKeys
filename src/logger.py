import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

DEFAULT_LOG_FILE = "app.log"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 5
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

_logger: Optional[logging.Logger] = None


def setup_logging(
    log_file: str = os.getenv("LOG_FILE", DEFAULT_LOG_FILE),
) -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(DEFAULT_FORMAT)

    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=DEFAULT_MAX_BYTES, backupCount=DEFAULT_BACKUP_COUNT, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except PermissionError:
        logger.warning(f"Unable to create/access log file: {log_file}")

    logger.propagate = False

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger
