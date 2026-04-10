"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIGUN_", case_sensitive=False)

    API_SECRET_KEY: str = "changeme"
    MAX_RETRIES: int = 3
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "AI Minigun"
    APP_VERSION: str = "0.1.0"


settings = Settings()
