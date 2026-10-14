"""Настройка логирования приложения."""

import logging
from logging.config import dictConfig


def configure_logging() -> None:
    """Настроить корневой логгер и приглушить access-логи uvicorn."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {"handlers": ["console"], "level": "INFO"},
        }
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
