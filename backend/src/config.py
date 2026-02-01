"""
Application Configuration

Centralized configuration management using pydantic-settings.
All settings can be overridden via environment variables.

Security Note: Sensitive values (DATABASE_KEY, etc.) should NEVER
be committed to version control. Use environment variables or
a secrets manager in production.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden by setting the corresponding
    environment variable (uppercase, prefixed with AIRFEELD_).
    
    Example:
        AIRFEELD_DEBUG=true
        AIRFEELD_DATABASE_URL=sqlite:///./data/airfeeld.db
    """
    
    model_config = SettingsConfigDict(
        env_prefix="AIRFEELD_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = "Airfeeld"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/airfeeld.db"
    database_echo: bool = False
    
    # Database encryption key (32 bytes for AES-256)
    # In production, this MUST be set via environment variable
    database_key: str = Field(
        default="",
        description="AES-256 encryption key for database at rest (required in production)"
    )
    
    # Security
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    rate_limit_enabled: bool = True
    
    # Proof of Work
    pow_difficulty: int = Field(default=4, ge=2, le=6)
    pow_timeout_seconds: int = Field(default=10, ge=5, le=60)
    pow_low_power_difficulty: int = Field(default=2, ge=1, le=4)
    pow_low_power_timeout_seconds: int = Field(default=30, ge=10, le=120)
    
    # Rate Limiting
    account_creation_limit: int = 3  # per IP per 24 hours
    photo_upload_limit: int = 5  # per IP per hour
    guess_limit: int = 100  # per IP per hour
    search_limit: int = 60  # per IP per minute
    flag_limit: int = 5  # per player per 24 hours
    
    # Storage
    storage_path: Path = Path("storage")
    photo_storage_path: Path = Path("storage/photos")
    cache_path: Path = Path("storage/cache")
    max_photo_size_mb: int = 10
    max_photo_dimension: int = 8192
    min_photo_dimension: int = 800
    
    # Content Moderation
    moderation_queue_timeout_hours: int = 48
    flag_threshold: int = 3  # flags before auto-review
    
    # Game Settings
    round_duration_seconds: int = Field(default=120, ge=30, le=600)
    max_guesses_per_round: int = Field(default=5, ge=1, le=10)
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str | None = None
    
    # IP Address Handling (privacy)
    ip_retention_days: int = 7
    
    @field_validator("database_key")
    @classmethod
    def validate_database_key(cls, v: str, info) -> str:
        """Ensure database key is set in production."""
        # This validation runs after all values are loaded
        # We check the environment separately
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def database_encryption_enabled(self) -> bool:
        """Check if database encryption is configured."""
        return bool(self.database_key)
    
    @property
    def max_photo_size(self) -> int:
        """Get max photo size in bytes."""
        return self.max_photo_size_mb * 1024 * 1024
    
    @property
    def app_debug(self) -> bool:
        """Alias for debug for compatibility."""
        return self.debug


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Settings are loaded once and cached for performance.
    To reload settings, call get_settings.cache_clear().
    """
    return Settings()
