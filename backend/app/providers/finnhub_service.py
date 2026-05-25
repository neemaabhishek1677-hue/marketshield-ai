"""
Finnhub.io integration for market data, quotes, and news.
Implements MarketDataProvider, NewsProvider interfaces.

Rate limits: Free tier ~60 req/min. Cache aggressively.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.core.config import get_settings
from app.providers.base import (
    MarketBar,
    MarketDataProvider,
    NewsItem,
    NewsProvider,
    ProviderError,
    ProviderRateLimitError,
    Quote,
    CompanyInfo,
)

logger = logging.getLogger(__name__)


class FinnhubService(MarketDataProvider, NewsProvider):
    """Finnhub provider for market data and news."""

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.finnhub_api_key
        if not self.api_key:
            logger.warning("FINNHUB_API_KEY not set. Finnhub integration disabled.")
        self.client = httpx.AsyncClient(timeout=30)

    async def _request(self, endpoint: str, params: dict) -> dict:
        """Make a request to Finnhub API."""
        if not self.api_key:
            raise ProviderError("Finnhub API key not configured")

        params["token"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ProviderRateLimitError(
                    f"Finnhub rate limit exceeded: {e.response.text}"
                )
            logger.error(f"Finnhub API error: {e.response.status_code} {e.response.text}")
            raise ProviderError(f"Finnhub API error: {e}") from e
        except Exception as e:
            logger.error(f"Finnhub request failed: {e}")
            raise ProviderError(f"Finnhub request failed: {e}") from e

    async def get_historical_bars(
        self, symbol: str, days: int = 30
    ) -> list[MarketBar]:
        """
        Fetch daily OHLCV bars via Finnhub candles endpoint.
        Returns up to `days` of historical data.
        """
        try:
            # Finnhub candles: resolution='D' for daily
            response = await self._request(
                "stock/candle",
                {
                    "symbol": symbol.upper(),
                    "resolution": "D",
                    "count": days,
                },
            )

            if response.get("s") == "no_data":
                logger.info(f"No candle data for {symbol}")
                return []

            bars = []
            if response.get("t"):  # timestamps
                timestamps = response["t"]
                opens = response.get("o", [])
                highs = response.get("h", [])
                lows = response.get("l", [])
                closes = response.get("c", [])
                volumes = response.get("v", [])

                for i, ts in enumerate(timestamps):
                    bar = MarketBar(
                        symbol=symbol.upper(),
                        timestamp=datetime.fromtimestamp(ts),
                        open=opens[i] if i < len(opens) else 0,
                        high=highs[i] if i < len(highs) else 0,
                        low=lows[i] if i < len(lows) else 0,
                        close=closes[i] if i < len(closes) else 0,
                        volume=volumes[i] if i < len(volumes) else 0,
                        provider="finnhub",
                        source_id=f"finnhub-candle-{symbol}-{ts}",
                    )
                    bars.append(bar)

            return bars
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch historical bars for {symbol}: {e}")
            raise ProviderError(f"Failed to fetch historical bars: {e}") from e

    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Fetch current quote using Finnhub quote endpoint."""
        try:
            response = await self._request(
                "quote",
                {"symbol": symbol.upper()},
            )

            if not response or all(v is None for v in response.values()):
                logger.info(f"No quote data for {symbol}")
                return None

            return Quote(
                symbol=symbol.upper(),
                timestamp=datetime.fromtimestamp(response.get("t", datetime.now().timestamp())),
                price=response.get("c", 0),  # current price
                bid=response.get("bp"),  # bid price
                ask=response.get("ap"),  # ask price
                volume=response.get("v"),  # last volume
                provider="finnhub",
                source_id=f"finnhub-quote-{symbol}",
            )
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch quote for {symbol}: {e}")
            raise ProviderError(f"Failed to fetch quote: {e}") from e

    async def get_intraday_bars(
        self, symbol: str, days: int = 1, interval_minutes: int = 60
    ) -> list[MarketBar]:
        """
        Fetch intraday bars (optional for Finnhub).
        Resolution: 1, 5, 15, 30, 60 minutes.
        """
        try:
            resolution_map = {1: "1", 5: "5", 15: "15", 30: "30", 60: "60"}
            resolution = resolution_map.get(interval_minutes, "60")

            response = await self._request(
                "stock/candle",
                {
                    "symbol": symbol.upper(),
                    "resolution": resolution,
                    "count": days * 24,  # rough estimate
                },
            )

            if response.get("s") == "no_data":
                logger.info(f"No intraday data for {symbol}")
                return []

            bars = []
            if response.get("t"):
                timestamps = response["t"]
                opens = response.get("o", [])
                highs = response.get("h", [])
                lows = response.get("l", [])
                closes = response.get("c", [])
                volumes = response.get("v", [])

                for i, ts in enumerate(timestamps):
                    bar = MarketBar(
                        symbol=symbol.upper(),
                        timestamp=datetime.fromtimestamp(ts),
                        open=opens[i] if i < len(opens) else 0,
                        high=highs[i] if i < len(highs) else 0,
                        low=lows[i] if i < len(lows) else 0,
                        close=closes[i] if i < len(closes) else 0,
                        volume=volumes[i] if i < len(volumes) else 0,
                        provider="finnhub",
                        source_id=f"finnhub-intraday-{symbol}-{ts}",
                    )
                    bars.append(bar)

            return bars
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch intraday bars for {symbol}: {e}")
            raise ProviderError(f"Failed to fetch intraday bars: {e}") from e

    async def get_news_for_symbol(
        self, symbol: str, days: int = 30
    ) -> list[NewsItem]:
        """Fetch company news for a symbol."""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")

            response = await self._request(
                "company-news",
                {
                    "symbol": symbol.upper(),
                    "from": from_date,
                    "to": to_date,
                },
            )

            if not isinstance(response, list):
                logger.warning(f"Unexpected response format for news: {response}")
                return []

            news_items = []
            for item in response[:100]:  # Limit to recent 100
                try:
                    news = NewsItem(
                        symbol=symbol.upper(),
                        headline=item.get("headline", ""),
                        url=item.get("url"),
                        published_at=datetime.fromtimestamp(item.get("datetime", 0)),
                        summary=item.get("summary"),
                        source=item.get("source", ""),
                        provider="finnhub",
                        source_id=f"finnhub-news-{item.get('id')}",
                    )
                    news_items.append(news)
                except Exception as e:
                    logger.warning(f"Failed to parse news item: {e}")
                    continue

            return news_items
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch news for {symbol}: {e}")
            raise ProviderError(f"Failed to fetch news: {e}") from e

    async def search_news(self, query: str, days: int = 30) -> list[NewsItem]:
        """Search for news by keyword."""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")

            response = await self._request(
                "news",
                {
                    "category": "general",
                    "minId": 0,
                },
            )

            if not isinstance(response, list):
                logger.warning(f"Unexpected response format for search: {response}")
                return []

            news_items = []
            for item in response[:50]:  # Limit results
                try:
                    # Attempt to match query in headline
                    headline = item.get("headline", "").lower()
                    if query.lower() not in headline:
                        continue

                    news = NewsItem(
                        symbol="",  # General search doesn't target specific symbol
                        headline=item.get("headline", ""),
                        url=item.get("url"),
                        published_at=datetime.fromtimestamp(item.get("datetime", 0)),
                        summary=item.get("summary"),
                        source=item.get("source", ""),
                        provider="finnhub",
                        source_id=f"finnhub-search-{item.get('id')}",
                    )
                    news_items.append(news)
                except Exception as e:
                    logger.warning(f"Failed to parse search result: {e}")
                    continue

            return news_items
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Failed to search news: {e}")
            raise ProviderError(f"Failed to search news: {e}") from e

    async def close(self):
        """Clean up HTTP client."""
        await self.client.aclose()
