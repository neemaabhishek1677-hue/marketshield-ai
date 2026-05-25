"""
Scheduler service for automated ingestion pipelines.
Uses APScheduler for lightweight task scheduling.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.services.ingestion import (
    MarketIngestionService,
    NewsIngestionService,
    FilingsIngestionService,
)

logger = logging.getLogger(__name__)


class IngestionScheduler:
    """Manage scheduled ingestion jobs."""

    def __init__(self):
        self.settings = get_settings()
        self.scheduler = AsyncIOScheduler()
        self.market_service = MarketIngestionService()
        self.news_service = NewsIngestionService()
        self.filings_service = FilingsIngestionService()
        self._initialized = False

    async def initialize(self, db_session_factory):
        """
        Initialize and start the scheduler.
        Call this during app startup.
        """
        if self._initialized:
            return

        self.db_factory = db_session_factory

        if self.settings.market_sync_enabled:
            self.scheduler.add_job(
                self._sync_market_job,
                IntervalTrigger(minutes=self.settings.market_sync_interval),
                id="market_sync",
                name="Market Data Sync",
                replace_existing=True,
            )
            logger.info(
                f"Scheduled market sync every {self.settings.market_sync_interval} minutes"
            )

        if self.settings.news_sync_enabled:
            self.scheduler.add_job(
                self._sync_news_job,
                IntervalTrigger(minutes=self.settings.news_sync_interval),
                id="news_sync",
                name="News Sync",
                replace_existing=True,
            )
            logger.info(
                f"Scheduled news sync every {self.settings.news_sync_interval} minutes"
            )

        if self.settings.filings_sync_enabled:
            self.scheduler.add_job(
                self._sync_filings_job,
                IntervalTrigger(minutes=self.settings.filings_sync_interval),
                id="filings_sync",
                name="Filings Sync",
                replace_existing=True,
            )
            logger.info(
                f"Scheduled filings sync every {self.settings.filings_sync_interval} minutes"
            )

        try:
            self.scheduler.start()
            self._initialized = True
            logger.info("Ingestion scheduler started")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    async def _sync_market_job(self):
        """Market sync job."""
        try:
            async with self.db_factory() as db:
                logger.info("Running scheduled market sync...")
                await self.market_service.sync_market_data(db)
        except Exception as e:
            logger.error(f"Scheduled market sync failed: {e}")

    async def _sync_news_job(self):
        """News sync job."""
        try:
            async with self.db_factory() as db:
                logger.info("Running scheduled news sync...")
                await self.news_service.sync_news(db)
        except Exception as e:
            logger.error(f"Scheduled news sync failed: {e}")

    async def _sync_filings_job(self):
        """Filings sync job."""
        try:
            async with self.db_factory() as db:
                logger.info("Running scheduled filings sync...")
                await self.filings_service.sync_filings(db)
        except Exception as e:
            logger.error(f"Scheduled filings sync failed: {e}")

    async def shutdown(self):
        """Shutdown the scheduler and cleanup."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Ingestion scheduler shut down")

        await self.market_service.close()
        await self.news_service.close()
        await self.filings_service.close()
