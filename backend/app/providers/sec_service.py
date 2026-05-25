"""
SEC EDGAR integration for filings and company information.
Implements FilingsProvider interface.

API: https://data.sec.gov/api/xbrl/
No API key required; must send valid User-Agent header.
Rate limits: ~10 req/sec (from data.sec.gov docs).
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.core.config import get_settings
from app.providers.base import (
    FilingEvent,
    FilingsProvider,
    ProviderError,
    ProviderRateLimitError,
    CompanyInfo,
)

logger = logging.getLogger(__name__)


class SECEDGARService(FilingsProvider):
    """SEC EDGAR provider for filings and company information."""

    XBRL_API_BASE = "https://data.sec.gov/api/xbrl"
    CIK_LOOKUP_URL = "https://www.sec.gov/files/company_tickers.json"
    FILINGS_URL = "https://data.sec.gov/submissions"

    def __init__(self):
        self.settings = get_settings()
        self.user_agent = self.settings.sec_user_agent
        self.client = httpx.AsyncClient(timeout=30)
        self._cik_cache = {}  # symbol -> CIK lookup cache

    async def _request(self, url: str, headers: Optional[dict] = None) -> dict:
        """Make HTTP request to SEC endpoint."""
        try:
            req_headers = headers or {}
            if "User-Agent" not in req_headers:
                req_headers["User-Agent"] = self.user_agent

            response = await self.client.get(url, headers=req_headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ProviderRateLimitError(
                    f"SEC rate limit exceeded: {e.response.text}"
                )
            logger.error(f"SEC API error: {e.response.status_code} {e.response.text}")
            raise ProviderError(f"SEC API error: {e}") from e
        except Exception as e:
            logger.error(f"SEC request failed: {e}")
            raise ProviderError(f"SEC request failed: {e}") from e

    async def _lookup_cik(self, symbol: str) -> Optional[str]:
        """
        Lookup CIK (Central Index Key) for a symbol.
        Caches locally to avoid repeated lookups.
        """
        symbol = symbol.upper()
        if symbol in self._cik_cache:
            return self._cik_cache[symbol]

        try:
            tickers = await self._request(self.CIK_LOOKUP_URL)
            for cik_str, company in tickers.items():
                if company.get("ticker", "").upper() == symbol:
                    cik = str(company["cik_str"]).zfill(10)
                    self._cik_cache[symbol] = cik
                    return cik
            logger.warning(f"CIK lookup failed for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Failed to lookup CIK for {symbol}: {e}")
            return None

    async def get_filings_for_symbol(
        self, symbol: str, days: int = 365, filing_types: Optional[list[str]] = None
    ) -> list[FilingEvent]:
        """
        Fetch SEC filings (10-K, 10-Q, 8-K, etc.) for a symbol.
        filing_types: e.g., ["10-K", "10-Q", "8-K"]. If None, fetch all.
        """
        try:
            cik = await self._lookup_cik(symbol)
            if not cik:
                logger.info(f"Could not find CIK for {symbol}")
                return []

            # Fetch submissions data for this company
            url = f"{self.FILINGS_URL}/CIK{cik}.json"
            data = await self._request(url)

            filings = []
            cutoff_date = datetime.now() - timedelta(days=days)

            # Process recent filings
            filings_data = data.get("filings", {}).get("recent", {})
            accession_numbers = filings_data.get("accessionNumber", [])
            form_types = filings_data.get("form", [])
            filing_dates = filings_data.get("filingDate", [])
            report_dates = filings_data.get("reportDate", [])

            for idx, form_type in enumerate(form_types):
                # Filter by type if specified
                if filing_types and form_type not in filing_types:
                    continue

                try:
                    filing_date_str = filing_dates[idx] if idx < len(filing_dates) else None
                    report_date_str = report_dates[idx] if idx < len(report_dates) else None

                    if filing_date_str:
                        filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d")
                        if filing_date < cutoff_date:
                            continue

                    report_date = None
                    if report_date_str:
                        report_date = datetime.strptime(report_date_str, "%Y-%m-%d")

                    accession = accession_numbers[idx] if idx < len(accession_numbers) else ""
                    # Convert accession format: 0001000025-22-000051 -> use as-is
                    filing_url = f"https://www.sec.gov/Archives/edgar/form/{accession.replace('-', '')}"

                    # Determine event type based on form
                    event_type = self._classify_form_type(form_type)

                    event = FilingEvent(
                        symbol=symbol.upper(),
                        event_type=form_type,  # 10-K, 10-Q, 8-K, etc.
                        event_date=report_date or filing_date,
                        filing_date=filing_date,
                        title=f"{form_type} Filing",
                        filing_url=filing_url,
                        provider="sec_edgar",
                        source_id=f"sec-{accession}",
                    )
                    filings.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse filing entry: {e}")
                    continue

            return filings
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch filings for {symbol}: {e}")
            raise ProviderError(f"Failed to fetch filings: {e}") from e

    async def get_company_info(self, symbol: str) -> Optional[CompanyInfo]:
        """
        Fetch company metadata from SEC.
        """
        try:
            cik = await self._lookup_cik(symbol)
            if not cik:
                logger.info(f"Could not find CIK for {symbol}")
                return None

            # Fetch company facts data
            url = f"{self.XBRL_API_BASE}/companyfacts/CIK{cik}.json"
            data = await self._request(url)

            # Extract company name and basic info
            entity_name = data.get("entityName", symbol)
            
            # Try to extract sector and industry from filings
            sector = None
            industry = None
            
            # For now, use basic company info from submission data
            company = CompanyInfo(
                symbol=symbol.upper(),
                name=entity_name,
                sector=sector,
                industry=industry,
                provider="sec_edgar",
            )
            return company
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch company info for {symbol}: {e}")
            # Return basic info even if detailed lookup fails
            return CompanyInfo(
                symbol=symbol.upper(),
                name=symbol,
                provider="sec_edgar",
            )

    @staticmethod
    def _classify_form_type(form_type: str) -> str:
        """Classify filing form type for event categorization."""
        form_type = form_type.strip().upper()

        if form_type in ["10-K", "10-K/A"]:
            return "annual_report"
        elif form_type in ["10-Q", "10-Q/A"]:
            return "quarterly_report"
        elif form_type in ["8-K"]:
            return "current_report"
        elif form_type.startswith("4"):
            return "insider_trading"
        elif form_type == "DEF 14A":
            return "proxy_statement"
        elif form_type == "S-1":
            return "ipo"
        else:
            return "filing"

    async def close(self):
        """Clean up HTTP client."""
        await self.client.aclose()
