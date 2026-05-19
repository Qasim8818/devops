"""
Centralized logging configuration with Loki integration
"""

import sys
import logging
import os
from loguru import logger as loguru_logger

from backend.config import get_settings


def setup_logging():
    """Configure logging with Loki integration"""
    settings = get_settings()

    loguru_logger.remove()

    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    os.makedirs("logs", exist_ok=True)
    loguru_logger.add(
        "logs/devsecops.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG",
        rotation="500 MB",
        retention="7 days",
    )

    if settings.LOKI_URL:
        try:
            loguru_logger.add(
                lambda msg: _send_to_loki(msg, settings),
                format="{message}",
                level=settings.LOG_LEVEL,
            )
        except Exception as e:
            loguru_logger.warning(f"Failed to configure Loki: {e}")

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    return loguru_logger


def _send_to_loki(message, settings):
    """Send log to Loki (placeholder for actual implementation)"""
    # In production, implement actual Loki sender
    pass
