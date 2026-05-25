"""Providers package — real-data source integrations."""

from app.providers.base import (
    CompanyInfo,
    FilingEvent,
    FilingsProvider,
    MarketBar,
    MarketDataProvider,
    NewsItem,
    NewsProvider,
    ProviderError,
    ProviderNotFoundError,
    ProviderRateLimitError,
    Quote,
)
from app.providers.finnhub_service import FinnhubService
from app.providers.sec_service import SECEDGARService
from app.providers.polygon_service import PolygonService
from app.providers.alpha_vantage_service import AlphaVantageService
from app.providers.gdelt_service import GDELTService

__all__ = [
    # Abstractions
    "MarketDataProvider",
    "NewsProvider",
    "FilingsProvider",
    "MarketBar",
    "Quote",
    "NewsItem",
    "FilingEvent",
    "CompanyInfo",
    # Exceptions
    "ProviderError",
    "ProviderRateLimitError",
    "ProviderNotFoundError",
    # Services
    "FinnhubService",
    "SECEDGARService",
    "PolygonService",
    "AlphaVantageService",
    "GDELTService",
]
