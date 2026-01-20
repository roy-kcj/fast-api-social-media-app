"""
Application configuration using Pydantic Settings.

Loads from environment variables and .env file.
Works with both SQLite (local dev) and PostgreSQL (Docker/production).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Priority order (highest to lowest):
    1. Environment variables
    2. .env file
    3. Default values below
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars
    )

    app_name: str = "FastAPI Social App"
    debug: bool = False
    # SQLite (local development without Docker):
    #   DATABASE_URL=sqlite://db.sqlite3
    #
    # PostgreSQL (Docker / production):
    #   DATABASE_URL=postgres://user:password@host:5432/dbname
    #
    # The docker-compose.yml sets this automatically
    database_url: str = "sqlite://db.sqlite3"
    redis_url: str = "redis://localhost:6379/0"
    
    secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using @lru_cache means settings are only loaded once,
    not on every request.
    """
    return Settings()