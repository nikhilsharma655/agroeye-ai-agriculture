"""
Centralized application configuration loaded from environment variables.
Never hardcode secrets — everything here is sourced from `.env` / the
process environment via pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "AgroEye"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api"

    DATABASE_URL: str = "sqlite:///./agroeye.db"

    JWT_SECRET_KEY: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    N8N_BASE_URL: str = "http://localhost:5678"
    N8N_FARM_ALERT_WEBHOOK_URL: str = ""
    N8N_IRRIGATION_ALERT_WEBHOOK_URL: str = ""
    N8N_RECOMMENDATION_WEBHOOK_URL: str = ""
    N8N_WEBHOOK_SHARED_SECRET: str = "insecure-dev-webhook-secret"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
