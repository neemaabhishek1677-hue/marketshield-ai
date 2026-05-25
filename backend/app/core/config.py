from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MarketShield AI"
    debug: bool = True
    # SQLite by default — works without Docker or PostgreSQL
    database_url: str = "sqlite+aiosqlite:///./data/marketshield.db"
    database_url_sync: str = "sqlite:///./data/marketshield.db"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    ml_model_path: str = "./data/models"
    seed_default_days: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
