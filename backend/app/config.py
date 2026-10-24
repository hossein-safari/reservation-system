from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEVELOPMENT_KEY = "local-development-only-change-this-secret-key"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    app_secret_key: str = Field(default=DEVELOPMENT_KEY, min_length=32)
    database_url: str = "sqlite:///./reservation.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]
    access_token_minutes: int = Field(default=30, ge=1, le=1440)

    @model_validator(mode="after")
    def production_secret(self) -> "Settings":
        if self.app_env == "production" and self.app_secret_key == DEVELOPMENT_KEY:
            raise ValueError("APP_SECRET_KEY must be changed in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
