"""
Application configuration powered by environment variables.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration for the RiskOps Demo Stack.
    """

    app_name: str = "RiskOps Demo Stack"
    environment: str = "local"
    database_url: str = "sqlite:///./transactions.db"
    redis_url: str = "redis://localhost:6379/0"
    feature_cache_ttl_seconds: int = 300
    high_amount_threshold: float = 500.0
    high_amount_decline_rate: float = 0.30
    random_decline_rate: float = 0.10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance so FastAPI dependencies stay lightweight.
    """

    return Settings()
