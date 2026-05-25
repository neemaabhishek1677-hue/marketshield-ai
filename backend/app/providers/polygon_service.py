"""
Polygon.io integration for real-time market data and quotes.
Implements MarketDataProvider interface.

Free tier and paid tiers available.
WebSocket streaming for live quotes optional.
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


class PolygonService(MarketDataProvider):
    """Polygon.io provider for market data."""

    BASE_URL = "https://api.polygon.io"

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.polygon_api_key
        if not self.api_key:
            logger.warning("POLYGON_API_KEY not set. Polygon integration disabled.")
        self.client = httpx.AsyncClient(timeout=30)

    async def _request(self, endpoint: str, params: dict) -> dict:
        """Make a request to Polygon API."""
        if not self.api_key:
            raise ProviderError("Polygon API key not configured")

        params["apiKey"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ProviderRateLimitError(f"Polygon rate limit exceeded")
            logger.error(f"Polygon API error: {e.response.status_code}")
            raise ProviderError(f"Polygon API error: {e}") from e
        except Exception as e:
            logger.error(f"Polygon request failed: {e}")
            raise ProviderError(f"Polygon request failed: {e}") from e

    async def get_historical_bars(self, symbol: str, days: int = 30) -> list[MarketBar]:
        """Fetch daily bars from Polygon."""
        raise ProviderError("Polygon: get_historical_bars not yet implemented")

    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Fetch current quote from Polygon."""
        raise ProviderError("Polygon: get_quote not yet implemented")

    async def get_intraday_bars(
        self, symbol: str, days: int = 1, interval_minutes: int = 60
    ) -> list[MarketBar]:
        """Fetch intraday bars from Polygon."""
        raise ProviderError("Polygon: get_intraday_bars not yet implemented")

    async def close(self):
        """Clean up HTTP client."""
        await self.client.aclose()
