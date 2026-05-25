"""
Alpha Vantage integration for fallback historical data and indicators.
Implements MarketDataProvider interface.

Free tier with rate limits (~5 req/min).
"""

import logging
from typing import Optional

import httpx

from app.core.config import get_settings
from app.providers.base import (
    MarketBar,
    MarketDataProvider,
    Quote,
    ProviderError,
    ProviderRateLimitError,
)

logger = logging.getLogger(__name__)


class AlphaVantageService(MarketDataProvider):
    """Alpha Vantage provider for market data."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.alpha_vantage_api_key
        if not self.api_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set. Alpha Vantage disabled.")
        self.client = httpx.AsyncClient(timeout=30)

    async def _request(self, params: dict) -> dict:
        """Make a request to Alpha Vantage API."""
        if not self.api_key:
            raise ProviderError("Alpha Vantage API key not configured")

        params["apikey"] = self.api_key
        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ProviderRateLimitError("Alpha Vantage rate limit exceeded")
            logger.error(f"Alpha Vantage API error: {e.response.status_code}")
            raise ProviderError(f"Alpha Vantage API error: {e}") from e
        except Exception as e:
            logger.error(f"Alpha Vantage request failed: {e}")
            raise ProviderError(f"Alpha Vantage request failed: {e}") from e

    async def get_historical_bars(self, symbol: str, days: int = 30) -> list[MarketBar]:
        """Fetch daily bars from Alpha Vantage."""
        raise ProviderError("AlphaVantage: get_historical_bars not yet implemented")

    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Fetch current quote from Alpha Vantage."""
        raise ProviderError("AlphaVantage: get_quote not yet implemented")

    async def get_intraday_bars(
        self, symbol: str, days: int = 1, interval_minutes: int = 60
    ) -> list[MarketBar]:
        """Fetch intraday bars from Alpha Vantage."""
        raise ProviderError("AlphaVantage: get_intraday_bars not yet implemented")

    async def close(self):
        """Clean up HTTP client."""
        await self.client.aclose()
