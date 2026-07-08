from __future__ import annotations

from typing import Any

from adapters.business_directory.adapter import BusinessDirectoryAdapter
from models import Lead
from scrapers.base import BaseScraper


class BusinessDirectoryScraper(BusinessDirectoryAdapter, BaseScraper):
    """Legacy scraper wrapper kept for backward compatibility."""

    def __init__(self, category: str, location: str, **kwargs: Any) -> None:
        super().__init__(category=category, location=location, **kwargs)

    def scrape(self, *args: Any, **kwargs: Any) -> list[Lead]:
        return self.fetch(*args, **kwargs)
