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

    # ===== REAL DATA PROVIDER CONFIGURATION =====
    # Finnhub (stock candles, quotes, company news)
    finnhub_api_key: str = ""
    
    # SEC EDGAR (filings, company facts) - no key required, but user agent recommended
    sec_user_agent: str = "MarketShieldAI/1.0 demo@example.com"
    
    # Optional: Polygon.io (real-time streaming)
    polygon_api_key: str = ""
    
    # Optional: Alpha Vantage (fallback historical data)
    alpha_vantage_api_key: str = ""
    
    # Optional: GDELT (broader news/event analytics)
    gdelt_enabled: bool = False
    
    # Watchlist configuration
    default_watchlist: str = "AAPL,MSFT,NVDA,TSLA,AMZN"
    
    # Ingestion feature flags
    market_sync_enabled: bool = True
    news_sync_enabled: bool = True
    filings_sync_enabled: bool = True
    
    # Ingestion frequency (in minutes)
    market_sync_interval: int = 30
    news_sync_interval: int = 60
    filings_sync_interval: int = 1440  # daily
    
    # Cache TTL for API responses (in seconds)
    provider_cache_ttl: int = 300

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def watchlist(self) -> list[str]:
        return [t.strip().upper() for t in self.default_watchlist.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
