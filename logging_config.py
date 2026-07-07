"""
Logging Configuration Module
=============================

Sets up structured logging for the Lead Intelligence Platform.

Usage:
    from logging_config import setup_logging
    setup_logging(config.logging)
    logger = logging.getLogger(__name__)
"""

import logging
import logging.handlers
from typing import Optional

from config import LoggingConfig


def setup_logging(logging_config: LoggingConfig) -> None:
    """
    Configure logging for the application.
    
    Sets up console and optional file logging with the specified format
    and level. Supports rotation for file handlers.
    
    Args:
        logging_config: LoggingConfig instance with logging settings.
    """
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, logging_config.level))
    
    # Create formatter
    formatter = logging.Formatter(logging_config.format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if logging_config.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            logging_config.log_file,
            maxBytes=logging_config.max_bytes,
            backupCount=logging_config.backup_count,
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.
    
    Args:
        name: Module name (typically __name__).
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
