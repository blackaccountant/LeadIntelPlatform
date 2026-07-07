from __future__ import annotations

import abc
import logging
import re
import time
from logging import LoggerAdapter
from typing import Any
from urllib.parse import ParseResult, urlparse, urlunparse

import requests
from requests import Response, Session
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from logging_config import get_logger
from models import Lead


class ScraperError(Exception):
    """Generic scraper error for retry and network failures."""


class BaseScraper(abc.ABC):
    """Abstract base class for all Lead Intelligence Platform scrapers.

    This class provides shared infrastructure for HTTP session lifecycle,
    automatic retries, rate limiting, structured logging, and common data
    normalization helpers. All concrete scraper implementations must return
    a list of `Lead` objects.
    """

    STATUS_RETRYABLE = {429, 500, 502, 503, 504}
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    PHONE_PATTERN = re.compile(r"\d+")

    def __init__(
        self,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        rate_limit_per_minute: int = 60,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rate_limit_per_minute = max(rate_limit_per_minute, 0)
        self.headers = headers or {}
        self.session = self._create_session()
        self._last_request_at = 0.0
        self._logger = LoggerAdapter(
            get_logger(self.__class__.__name__),
            {"scraper": self.__class__.__name__},
        )

    def _create_session(self) -> Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "LeadIntelPlatform/1.0 (+https://example.com)",
            "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
        })
        session.headers.update(self.headers)
        return session

    def __enter__(self) -> BaseScraper:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()
        self._logger.debug("HTTP session closed")

    def _throttle(self) -> None:
        if self.rate_limit_per_minute <= 0:
            return
        interval = 60.0 / self.rate_limit_per_minute
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < interval:
            delay = interval - elapsed
            self._logger.debug("Rate limiting throttle", extra={"delay_seconds": delay})
            time.sleep(delay)

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Response:
        """Perform an HTTP request with retry logic and rate limiting."""
        self._throttle()
        for attempt in range(1, self.max_retries + 1):
            try:
                self._logger.debug(
                    "HTTP request attempt",
                    extra={"method": method, "url": url, "attempt": attempt},
                )
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs,
                )
                self._last_request_at = time.monotonic()
                if response.status_code in self.STATUS_RETRYABLE:
                    raise HTTPError(
                        f"Retryable status code: {response.status_code}",
                        response=response,
                    )
                response.raise_for_status()
                return response
            except (Timeout, ConnectionError, HTTPError, RequestException) as exc:
                should_retry = attempt < self.max_retries and self._is_retryable(exc)
                self._logger.warning(
                    "HTTP request failed",
                    extra={
                        "url": url,
                        "attempt": attempt,
                        "error": exc.__class__.__name__,
                        "retry": should_retry,
                    },
                )
                if not should_retry:
                    raise ScraperError(
                        f"Request failed after {attempt} attempts: {url}"
                    ) from exc
                sleep_seconds = self._backoff_seconds(attempt, response=locals().get("response"))
                self._logger.debug(
                    "Retrying HTTP request",
                    extra={"url": url, "attempt": attempt, "sleep_seconds": sleep_seconds},
                )
                time.sleep(sleep_seconds)
        raise ScraperError(f"Exhausted retries for URL: {url}")

    def _backoff_seconds(self, attempt: int, response: Response | None = None) -> float:
        if response is not None:
            retry_after = self._extract_retry_after(response)
            if retry_after is not None:
                return retry_after
        return self.backoff_factor * (2 ** (attempt - 1))

    def _extract_retry_after(self, response: Response) -> float | None:
        retry_after = response.headers.get("Retry-After")
        if retry_after is None:
            return None
        try:
            return float(retry_after)
        except ValueError:
            return None

    def _is_retryable(self, exc: BaseException) -> bool:
        if isinstance(exc, HTTPError) and getattr(exc, "response", None) is not None:
            return exc.response.status_code in self.STATUS_RETRYABLE
        return isinstance(exc, (Timeout, ConnectionError))

    def fetch_html(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> str:
        """Fetch HTML content from the given URL."""
        request_headers = {"Accept": "text/html,application/xhtml+xml"}
        if headers:
            request_headers.update(headers)
        response = self._request("GET", url, params=params, headers=request_headers)
        return response.text

    def fetch_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Fetch JSON from the given URL and return the parsed body."""
        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        response = self._request("GET", url, params=params, headers=request_headers)
        return response.json()

    def normalize_phone(self, phone: str | None) -> str | None:
        """Normalize phone numbers to digits-only format.

        Example:
            +1 (415) 555-1234 -> 14155551234
        """
        if not phone:
            return None
        digits = "".join(self.PHONE_PATTERN.findall(phone))
        if len(digits) == 11 and digits.startswith("1"):
            return digits
        if len(digits) == 10:
            return f"1{digits}"
        return digits if digits else None

    def normalize_url(self, url: str | None) -> str | None:
        """Normalize a URL by ensuring a scheme and trimming whitespace."""
        if not url:
            return None
        normalized = url.strip()
        if not normalized:
            return None
        parsed = urlparse(normalized, scheme="https")
        if not parsed.netloc:
            parsed = urlparse(f"https://{normalized}", scheme="https")
        if not parsed.netloc:
            return None
        safe_url = urlunparse(
            ParseResult(
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path or "",
                parsed.params or "",
                parsed.query or "",
                parsed.fragment or "",
            )
        )
        return safe_url

    def normalize_email(self, email: str | None) -> str | None:
        """Normalize email addresses to lowercase and validate format."""
        if not email:
            return None
        normalized = email.strip().lower()
        return normalized if self.EMAIL_PATTERN.match(normalized) else None

    @abc.abstractmethod
    def scrape(self, *args: Any, **kwargs: Any) -> list[Lead]:
        """Scrape leads from a source and return a list of Lead objects."""
        raise NotImplementedError("Scraper subclasses must implement scrape()")
