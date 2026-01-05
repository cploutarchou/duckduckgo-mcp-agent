"""
Configuration management for the MCP Web Search Agent.

This module provides environment-based configuration with validation
using Pydantic settings. All settings are prefixed with 'MCP_' and
can be loaded from environment variables or a .env file.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Configuration is loaded from environment variables with the 'MCP_' prefix.
    For example, MCP_DEBUG=true sets the debug flag.

    All settings have sensible defaults suitable for production deployments.
    """

    # Application settings
    app_name: str = "MCP Web Search Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Search settings
    max_search_results: int = 10
    default_search_results: int = 5
    search_timeout: int = 30

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # in seconds

    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds
    cache_max_size: int = 1000

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None

    # CORS
    cors_enabled: bool = True
    cors_origins: list[str] = ["*"]

    # API key (optional, for future use)
    api_key: Optional[str] = None

    class Config:
        """Pydantic configuration for settings."""

        env_prefix = "MCP_"
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Retrieve the cached settings instance.

    Returns the same Settings instance for the entire application lifetime.
    Uses LRU cache to ensure configuration is loaded only once.

    Returns:
        Settings: The application configuration instance.
    """
    return Settings()
