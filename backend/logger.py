"""
Centralized logging configuration with Loki integration
"""

import sys
import logging
from loguru import logger as loguru_logger

from config import get_settings


def setup_logging():
    """Configure logging with Loki integration"""
    settings = get_settings()
    
    # Remove default handler
    loguru_logger.remove()
    
    # Add console handler with color
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Add file handler
    loguru_logger.add(
        f"logs/devsecops.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG",
        rotation="500 MB",
        retention="7 days",
    )
    
    # Add Loki handler if configured
    if settings.LOKI_URL:
        try:
            loguru_logger.add(
                lambda msg: _send_to_loki(msg, settings),
                format="{message}",
                level=settings.LOG_LEVEL,
            )
        except Exception as e:
            loguru_logger.warning(f"Failed to configure Loki: {e}")
    
    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    return loguru_logger


def _send_to_loki(message, settings):
    """Send log to Loki (placeholder for actual implementation)"""
    # In production, implement actual Loki sender
    pass
