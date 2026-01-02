"""Application settings using Pydantic"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application configuration

    Loads settings from environment variables or .env file.
    All settings have sensible defaults for development.
    """

    # Reddit API credentials (optional for Phase 1, can be empty)
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "redditsearch/0.1.0"

    # Search defaults
    DEFAULT_SUBREDDITS: List[str] = ["SaaS", "Entrepreneur", "startups"]
    DEFAULT_KEYWORDS: List[str] = ["pay for", "need a tool", "wish there was"]

    # Paths
    DATABASE_PATH: str = "data/redditsearch.db"
    OUTPUT_DIR: str = "output"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in .env
    )


def get_settings() -> Settings:
    """Get application settings

    This function creates a new Settings instance each time it's called.
    For production use, consider caching with lru_cache.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
