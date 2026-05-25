"""
Base abstractions for real-data providers.
All providers must implement these interfaces to ensure interchangeability.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MarketBar:
    """Normalized market bar (OHLCV) from any provider."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    provider: str
    source_id: Optional[str] = None  # For audit/deduplication


@dataclass
class Quote:
    """Normalized current quote."""
    symbol: str
    timestamp: datetime
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[float] = None
    provider: str = ""
    source_id: Optional[str] = None


@dataclass
class NewsItem:
    """Normalized news article."""
    symbol: str
    headline: str
    url: Optional[str]
    published_at: datetime
    summary: Optional[str] = None
    sentiment: Optional[str] = None  # "positive", "negative", "neutral"
    source: str = ""
    provider: str = ""
    source_id: Optional[str] = None


@dataclass
class FilingEvent:
    """Normalized SEC filing or corporate event."""
    symbol: str
    event_type: str  # "10-K", "10-Q", "8-K", "earnings", etc.
    event_date: datetime
    filing_date: Optional[datetime] = None
    title: Optional[str] = None
    filing_url: Optional[str] = None
    summary: Optional[str] = None
    provider: str = ""
    source_id: Optional[str] = None


@dataclass
class CompanyInfo:
    """Company metadata and facts."""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    employees: Optional[int] = None
    website: Optional[str] = None
    provider: str = ""


class MarketDataProvider(ABC):
    """Abstract base for market data providers (OHLCV, quotes)."""

    @abstractmethod
    async def get_historical_bars(
        self, symbol: str, days: int = 30
    ) -> list[MarketBar]:
        """Fetch historical daily market bars."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Fetch current quote."""
        pass

    @abstractmethod
    async def get_intraday_bars(
        self, symbol: str, days: int = 1, interval_minutes: int = 60
    ) -> list[MarketBar]:
        """Fetch intraday bars (optional, may not be supported by all providers)."""
        pass


class NewsProvider(ABC):
    """Abstract base for news data providers."""

    @abstractmethod
    async def get_news_for_symbol(
        self, symbol: str, days: int = 30
    ) -> list[NewsItem]:
        """Fetch news articles for a symbol."""
        pass

    @abstractmethod
    async def search_news(self, query: str, days: int = 30) -> list[NewsItem]:
        """Search for news by keyword."""
        pass


class FilingsProvider(ABC):
    """Abstract base for filings and corporate events."""

    @abstractmethod
    async def get_filings_for_symbol(
        self, symbol: str, days: int = 365, filing_types: Optional[list[str]] = None
    ) -> list[FilingEvent]:
        """Fetch filings for a symbol."""
        pass

    @abstractmethod
    async def get_company_info(self, symbol: str) -> Optional[CompanyInfo]:
        """Fetch company metadata."""
        pass


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when API rate limit is hit."""
    pass


class ProviderNotFoundError(ProviderError):
    """Raised when symbol/data is not found."""
    pass
