from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "pantau-duit"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = "dev_secret_key_change_in_production_32bytes_min_length_for_aes_gcm"

    DATABASE_URL: str = "postgresql+psycopg://galaxymacbook@localhost:5432/pantau_duit_db"
    ASYNC_DATABASE_URL: Optional[str] = "postgresql+asyncpg://galaxymacbook@localhost:5432/pantau_duit_db"

    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
