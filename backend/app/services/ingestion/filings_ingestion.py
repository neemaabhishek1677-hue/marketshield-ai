"""
SEC filings ingestion service.
Fetches real corporate filings and events from SEC EDGAR and stores in database.
"""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.models.entities import RealFilingEvent, IngestionRun
from app.providers.sec_service import SECEDGARService
from app.providers.base import ProviderError

logger = logging.getLogger(__name__)


class FilingsIngestionService:
    """Orchestrate filings data ingestion from SEC EDGAR."""

    def __init__(self):
        self.settings = get_settings()
        self.sec = SECEDGARService()

    async def sync_filings(
        self, db: AsyncSession, symbols: list[str] | None = None, days: int = 365
    ) -> dict:
        """
        Fetch SEC filings for symbols and store in database.
        Returns stats on ingestion run.
        """
        if symbols is None:
            symbols = self.settings.watchlist

        run = IngestionRun(
            ingestion_type="filings",
            provider="sec_edgar",
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
                logger.info(f"Fetching filings for {symbol}")
                filings = await self.sec.get_filings_for_symbol(symbol, days=days)

                for filing in filings:
                    try:
                        # Check if record already exists
                        existing = await db.execute(
                            select(RealFilingEvent).filter_by(source_id=filing.source_id)
                        )
                        if existing.scalar_one_or_none():
                            stats["records_updated"] += 1
                            continue

                        # Insert new record
                        new_filing = RealFilingEvent(
                            symbol=filing.symbol,
                            event_type=filing.event_type,
                            event_date=filing.event_date,
                            filing_date=filing.filing_date,
                            title=filing.title,
                            filing_url=filing.filing_url,
                            summary=filing.summary,
                            provider=filing.provider,
                            source_id=filing.source_id,
                        )
                        db.add(new_filing)
                        stats["records_created"] += 1
                    except Exception as e:
                        logger.error(f"Failed to ingest filing for {symbol}: {e}")
                        stats["records_skipped"] += 1
                        continue

                stats["symbols_processed"] += 1
            except ProviderError as e:
                logger.error(f"Provider error fetching filings for {symbol}: {e}")
                stats["errors"].append(f"{symbol}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error fetching filings for {symbol}: {e}")
                stats["errors"].append(f"{symbol}: {str(e)}")

        # Commit all inserts
        try:
            await db.commit()
            logger.info(f"Filings ingestion completed: {stats}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to commit filings data: {e}")
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
        await self.sec.close()
