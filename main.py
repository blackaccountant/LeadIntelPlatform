"""
Main Entry Point
================

Lead Intelligence Platform - AI-assisted lead generation system.

This module serves as the application entry point, initializing the
configuration, logging, and orchestrating the main application flow.
"""

import logging
import sys
from typing import Optional

from config import get_global_config, init_config
from logging_config import setup_logging, get_logger


logger = get_logger(__name__)


def main(args: Optional[list[str]] = None) -> int:
    """
    Main application entry point.
    
    Initializes configuration, sets up logging, and runs the application.
    
    Args:
        args: Optional command-line arguments (for testing).
        
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    try:
        # Initialize configuration
        config = init_config()
        
        # Set up logging
        setup_logging(config.logging)
        
        logger.info(f"Starting {config.app_name} v{config.app_version}")
        logger.info(f"Environment: {config.environment}")
        logger.debug(f"Debug mode: {config.debug}")
        
        # TODO: Implement main application logic
        # - Initialize database connection
        # - Set up service layer
        # - Run scraping pipeline
        # - Process enrichment
        # - Export results
        
        logger.info("Application initialized successfully")
        return 0
        
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
