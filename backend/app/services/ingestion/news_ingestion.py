"""
News ingestion service.
Fetches real company news from providers and stores in database.
"""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.models.entities import RealNews, IngestionRun
from app.providers.finnhub_service import FinnhubService
from app.providers.base import ProviderError

logger = logging.getLogger(__name__)


class NewsIngestionService:
    """Orchestrate news data ingestion from providers."""

    def __init__(self):
        self.settings = get_settings()
        self.finnhub = FinnhubService()

    async def sync_news(
        self, db: AsyncSession, symbols: list[str] | None = None, days: int = 30
    ) -> dict:
        """
        Fetch company news for symbols and store in database.
        Returns stats on ingestion run.
        """
        if symbols is None:
            symbols = self.settings.watchlist

        run = IngestionRun(
            ingestion_type="news",
            provider="finnhub",
            status="running",
            started_at=datetime.now(),
        )
        await db.add(run)
        await db.flush()
        run_id = run.id

        stats = {
            "run_id": run_id,
            "symbols_processed": 0,
            "records_created": 0,
            "records_updated": 0,
            "records_skipped": 0,
            "errors": [],
        }

        for symbol in symbols:
            try:
                logger.info(f"Fetching news for {symbol}")
                news_items = await self.finnhub.get_news_for_symbol(symbol, days=days)

                for news in news_items:
                    try:
                        # Check if record already exists
                        existing = await db.execute(
                            select(RealNews).filter_by(source_id=news.source_id)
                        )
                        if existing.scalar_one_or_none():
                            stats["records_updated"] += 1
                            continue

                        # Insert new record
                        new_news = RealNews(
                            symbol=news.symbol,
                            headline=news.headline,
                            url=news.url,
                            summary=news.summary,
                            published_at=news.published_at,
                            source=news.source,
                            provider=news.provider,
                            source_id=news.source_id,
                        )
                        db.add(new_news)
                        stats["records_created"] += 1
                    except Exception as e:
                        logger.error(f"Failed to ingest news for {symbol}: {e}")
                        stats["records_skipped"] += 1
                        continue

                stats["symbols_processed"] += 1
            except ProviderError as e:
                logger.error(f"Provider error fetching news for {symbol}: {e}")
                stats["errors"].append(f"{symbol}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error fetching news for {symbol}: {e}")
                stats["errors"].append(f"{symbol}: {str(e)}")

        # Commit all inserts
        try:
            await db.commit()
            logger.info(f"News ingestion completed: {stats}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to commit news data: {e}")
            stats["errors"].append(f"Commit failed: {str(e)}")

        # Update ingestion run status
        run.status = "success" if not stats["errors"] else "partial"
        run.symbols_processed = stats["symbols_processed"]
        run.records_created = stats["records_created"]
        run.records_updated = stats["records_updated"]
        run.records_skipped = stats["records_skipped"]
        run.error_message = "; ".join(stats["errors"]) if stats["errors"] else None
        run.completed_at = datetime.now()
        await db.merge(run)
        await db.commit()

        return stats

    async def close(self):
        """Clean up resources."""
        await self.finnhub.close()
