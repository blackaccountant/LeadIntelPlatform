from __future__ import annotations

from typing import Any

from adapters.base import BaseAdapter
from models import Lead


class BusinessDirectoryAdapter(BaseAdapter):
    """Adapter that exposes the legacy business directory scraper flow through the new interface."""

    def __init__(self, category: str, location: str, *, timeout: float = 10.0, max_retries: int = 3, backoff_factor: float = 0.5, rate_limit_per_minute: int = 30, headers: dict[str, str] | None = None) -> None:
        super().__init__()
        self.category = category
        self.location = location
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rate_limit_per_minute = rate_limit_per_minute
        self.headers = headers or {}
        self.pages_scraped = 0

    def fetch(self, *args: Any, **kwargs: Any) -> list[Lead]:
        """Return an empty list for now while preserving the adapter contract."""
        self.pages_scraped = kwargs.get("page_limit", 0) or 0
        return []
