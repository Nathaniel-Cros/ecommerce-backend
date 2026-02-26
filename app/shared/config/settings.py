"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="sqlite+pysqlite:///./dev.db",
        alias="DATABASE_URL",
    )
    env: Literal["dev", "test", "prod"] = Field(default="dev", alias="ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    mp_access_token: str | None = Field(default=None, alias="MP_ACCESS_TOKEN")
    mp_public_key: str | None = Field(default=None, alias="MP_PUBLIC_KEY")
    mp_webhook_url: str | None = Field(default=None, alias="MP_WEBHOOK_URL")
    mp_environment: Literal["sandbox", "prod"] = Field(
        default="sandbox",
        alias="MP_ENVIRONMENT",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
