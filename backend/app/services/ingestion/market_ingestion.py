"""
Market data ingestion service.
Fetches real market bars from providers and stores in database.
"""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy import insert, select

from app.core.config import get_settings
from app.models.entities import MarketBarDaily, IngestionRun
from app.providers.finnhub_service import FinnhubService
from app.providers.base import ProviderError

logger = logging.getLogger(__name__)


class MarketIngestionService:
    """Orchestrate market data ingestion from providers."""

    def __init__(self):
        self.settings = get_settings()
        self.finnhub = FinnhubService()

    async def sync_market_data(
        self, db: AsyncSession, symbols: list[str] | None = None, days: int = 30
    ) -> dict:
        """
        Fetch historical market bars for symbols and store in database.
        Returns stats on ingestion run.
        """
        if symbols is None:
            symbols = self.settings.watchlist

        run = IngestionRun(
            ingestion_type="market",
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
                logger.info(f"Fetching market data for {symbol}")
                bars = await self.finnhub.get_historical_bars(symbol, days=days)

                for bar in bars:
                    try:
                        # Check if record already exists
                        existing = await db.execute(
                            select(MarketBarDaily).filter_by(source_id=bar.source_id)
                        )
                        if existing.scalar_one_or_none():
                            stats["records_updated"] += 1
                            continue

                        # Insert new record
                        new_bar = MarketBarDaily(
                            symbol=bar.symbol,
                            date=bar.timestamp,
                            open=bar.open,
                            high=bar.high,
                            low=bar.low,
                            close=bar.close,
                            volume=bar.volume,
                            provider=bar.provider,
                            source_id=bar.source_id,
                        )
                        db.add(new_bar)
                        stats["records_created"] += 1
                    except Exception as e:
                        logger.error(f"Failed to ingest bar for {symbol}: {e}")
                        stats["records_skipped"] += 1
                        continue

                stats["symbols_processed"] += 1
            except ProviderError as e:
                logger.error(f"Provider error fetching {symbol}: {e}")
                stats["errors"].append(f"{symbol}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error fetching {symbol}: {e}")
                stats["errors"].append(f"{symbol}: {str(e)}")

        # Commit all inserts
        try:
            await db.commit()
            logger.info(f"Market ingestion completed: {stats}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to commit market data: {e}")
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
