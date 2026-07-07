from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models import Lead
from scrapers.base import BaseScraper, ScraperError
from scrapers.business_directory.constants import (
    BASE_URL,
    LISTING_SELECTOR,
    NEXT_PAGE_SELECTOR,
    SEARCH_PATH,
)
from scrapers.business_directory.parser import parse_listing


class BusinessDirectoryScraper(BaseScraper):
    """Scraper for the example business directory."""

    def __init__(
        self,
        category: str,
        location: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        rate_limit_per_minute: int = 30,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            rate_limit_per_minute=rate_limit_per_minute,
            headers=headers,
        )
        self.category = category
        self.location = location

    def scrape(self, page_limit: int = 5) -> list[Lead]:
        """Scrape business listings and return a list of Lead objects."""
        leads: list[Lead] = []
        next_page_url = urljoin(BASE_URL, SEARCH_PATH)
        page_count = 0

        while next_page_url and page_count < page_limit:
            page_count += 1
            try:
                self._logger.info("Processing page", extra={"page": page_count, "url": next_page_url})
                html = self.fetch_html(
                    next_page_url,
                    params={"category": self.category, "location": self.location},
                )
                page_leads, next_page_url = self._parse_page(html, next_page_url)
                leads.extend(page_leads)
            except ScraperError as exc:
                self._logger.error("Page fetch failed", exc_info=exc, extra={"url": next_page_url})
                break
            except Exception as exc:
                self._logger.warning("Non-fatal error processing page", exc_info=exc, extra={"page": page_count})
            if next_page_url:
                next_page_url = urljoin(BASE_URL, next_page_url)
        return leads

    def _parse_page(self, html: str, page_url: str) -> tuple[list[Lead], str | None]:
        soup = BeautifulSoup(html, "html.parser")
        listings = soup.select(LISTING_SELECTOR)
        leads: list[Lead] = []

        for listing in listings:
            try:
                lead = parse_listing(listing, page_url)
                if lead is not None:
                    lead.company.website = self.normalize_url(lead.company.website)
                    lead.contact.phone = self.normalize_phone(lead.contact.phone)
                    lead.company.name = lead.company.name.strip()
                    leads.append(lead)
            except Exception as exc:
                self._logger.warning(
                    "Bad listing skipped",
                    exc_info=exc,
                    extra={"page_url": page_url},
                )

        next_link = soup.select_one(NEXT_PAGE_SELECTOR)
        next_url = next_link["href"].strip() if next_link and next_link.has_attr("href") else None
        return leads, next_url
