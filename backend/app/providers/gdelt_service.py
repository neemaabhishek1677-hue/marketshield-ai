"""
GDELT (Global Database of Events, Language, and Tone) integration for broader
news/event analytics. Optional advanced provider for narrative analysis.
"""

import logging

from app.providers.base import ProviderError

logger = logging.getLogger(__name__)


class GDELTService:
    """GDELT provider for news events and analysis."""

    def __init__(self):
        logger.info("GDELT service initialized (stub - full implementation pending)")

    async def get_events_by_source(self, source: str, days: int = 30):
        """Fetch events by news source."""
        raise ProviderError("GDELT: get_events_by_source not yet implemented")

    async def get_events_by_tone(self, tone: str, days: int = 30):
        """Fetch events by tone (e.g., positive, negative)."""
        raise ProviderError("GDELT: get_events_by_tone not yet implemented")

    async def close(self):
        """Clean up resources."""
        pass
