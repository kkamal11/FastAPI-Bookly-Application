import re
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
USER_LOG_DIR = BASE_DIR / Path("logs/user_logs")


def sanitize_username(username: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", username)

_user_loggers = {}

def get_user_logger(username: str) -> logging.Logger:
    safe_username = sanitize_username(username)

    if safe_username in _user_loggers:
        return _user_loggers[safe_username]

    logger = logging.getLogger(f"user_{safe_username}")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        USER_LOG_DIR / f"{safe_username}.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=3
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    _user_loggers[safe_username] = logger
    return logger


