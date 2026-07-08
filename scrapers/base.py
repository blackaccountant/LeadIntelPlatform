from __future__ import annotations

import warnings
from typing import Any

from adapters.base import BaseAdapter
from models import Lead


class ScraperError(Exception):
    """Generic scraper error for retry and network failures."""


class BaseScraper(BaseAdapter):
    """Backward-compatible compatibility shim for legacy scraper imports."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn("BaseScraper is deprecated; use BaseAdapter instead.", DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    def scrape(self, *args: Any, **kwargs: Any) -> list[Lead]:
        """Compatibility entrypoint retained for older scraper implementations."""
        return self.fetch(*args, **kwargs)
