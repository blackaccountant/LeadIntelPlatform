"""
Configuration Module
====================

Centralized configuration management for the Lead Intelligence Platform.
Supports environment-based configuration with defaults for development.

Usage:
    from config import Config, get_config
    config = get_config()
    db_url = config.database_url
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: float = 30.0
    pool_recycle: int = 3600


@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class APIConfig:
    """External API configuration."""
    
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1


@dataclass
class EnrichmentConfig:
    """AI enrichment configuration."""
    
    enabled: bool = True
    model_provider: str = "openai"  # or "anthropic", "local", etc.
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


@dataclass
class Config:
    """Main application configuration."""
    
    # Application
    app_name: str = "Lead Intelligence Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    
    # Database
    database: DatabaseConfig = None
    
    # Logging
    logging: LoggingConfig = None
    
    # APIs
    api: APIConfig = None
    
    # Enrichment
    enrichment: EnrichmentConfig = None
    
    def __post_init__(self) -> None:
        """Initialize nested configs if not provided."""
        if self.database is None:
            self.database = DatabaseConfig(
                url=os.getenv(
                    "DATABASE_URL",
                    "sqlite:///./lead_intelligence.db"
                )
            )
        if self.logging is None:
            self.logging = LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                log_file=os.getenv("LOG_FILE", None)
            )
        if self.api is None:
            self.api = APIConfig()
        if self.enrichment is None:
            self.enrichment = EnrichmentConfig(
                api_key=os.getenv("ENRICHMENT_API_KEY")
            )


def get_config() -> Config:
    """
    Factory function to create and return application configuration.
    
    Configuration is built from environment variables with sensible defaults.
    Environment variable priorities:
    - ENVIRONMENT: "development", "staging", "production"
    - DEBUG: "true" or "false"
    - DATABASE_URL: Database connection string
    - LOG_LEVEL: Logging level
    - LOG_FILE: Optional log file path
    - ENRICHMENT_API_KEY: API key for enrichment service
    
    Returns:
        Config: Configured application settings.
    """
    environment = os.getenv("ENVIRONMENT", "development")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    config = Config(
        environment=environment,
        debug=debug or environment == "development",
    )
    
    return config


# Singleton instance
_config: Optional[Config] = None


def init_config(custom_config: Optional[Config] = None) -> Config:
    """
    Initialize the global configuration singleton.
    
    Args:
        custom_config: Optional custom Config instance for testing.
        
    Returns:
        Config: The initialized configuration.
    """
    global _config
    _config = custom_config or get_config()
    return _config


def get_global_config() -> Config:
    """
    Get the global configuration instance.
    Initializes if not already done.
    
    Returns:
        Config: The global configuration instance.
    """
    global _config
    if _config is None:
        _config = get_config()
    return _config
