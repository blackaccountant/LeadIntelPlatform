from __future__ import annotations

import os
import re
import time
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from adapters.base import AdapterError, BaseAdapter
from models import Company, Contact, Lead


class WebsiteAdapter(BaseAdapter):
    """Crawl a target company's website and convert discoveries into domain models."""

    INTERNAL_PATHS = ["/", "/about", "/contact", "/team", "/leadership", "/services"]
    EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
    PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
    SOCIAL_RE = re.compile(r"https?://(?:www\.)?(linkedin\.com|twitter\.com|x\.com|facebook\.com|github\.com|instagram\.com)[^\s\"'>]+", re.IGNORECASE)
    TECHNOLOGY_HINTS = ["python", "django", "flask", "fastapi", "react", "vue", "javascript", "typescript", "postgres", "mysql", "redis", "docker", "kubernetes", "aws", "azure", "gcp", "node", "nginx", "apache"]

    def __init__(
        self,
        *,
        timeout: int = 15,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        cache_ttl_seconds: int = 300,
        session: requests.Session | None = None,
    ) -> None:
        super().__init__()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache_ttl_seconds = cache_ttl_seconds
        self.session = session or requests.Session()
        self._cache: dict[str, tuple[float, list[Lead]]] = {}

    def fetch(self, *args: Any, **kwargs: Any) -> list[Lead]:
        target_url = kwargs.get("url") or args[0] if args else ""
        if not target_url:
            raise AdapterError("A website URL is required")

        normalized_url = self._normalize_url(target_url)
        cache_key = normalized_url
        cached = self._cache.get(cache_key)
        if cached is not None and (time.monotonic() - cached[0]) < self.cache_ttl_seconds:
            return list(cached[1])

        self._logger.info("Analyzing website", extra={"url": normalized_url})
        leads: list[Lead] = []
        pages: list[dict[str, Any]] = []
        for path in self.INTERNAL_PATHS:
            page_url = self._join_url(normalized_url, path)
            if not self._should_fetch(page_url):
                continue
            page = self._fetch_page(page_url)
            if page is None:
                continue
            pages.append(page)

        if not pages:
            return []

        page_data = self._merge_pages(pages)
        company = Company(
            name=page_data["company_name"],
            website=normalized_url,
            domain=self._extract_domain(normalized_url),
            industry=page_data["industry"],
        )
        contact = Contact(
            first_name="Website",
            last_name="Contact",
            email=page_data["emails"][0] if page_data["emails"] else None,
            phone=page_data["phones"][0] if page_data["phones"] else None,
            title="Website Contact",
            linkedin_url=page_data["social_links"][0] if page_data["social_links"] else None,
        )
        lead = Lead(
            company=company,
            contact=contact,
            source=f"website:{normalized_url}",
            industry=page_data["industry"],
            confidence_score=0.7,
            status="new",
            tags=self._normalize_tags(page_data["technologies"], page_data["social_links"]),
            notes=[page_data["meta_description"]],
        )
        leads.append(lead)
        self._cache[cache_key] = (time.monotonic(), leads)
        return leads

    def _fetch_page(self, url: str) -> dict[str, Any] | None:
        try:
            response = self._request(url)
        except Exception as exc:
            self._logger.warning("Website fetch failed", extra={"url": url, "error": str(exc)})
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        title = self._clean_text(soup.title.get_text()) if soup.title else ""
        meta_description = ""
        meta_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        if meta_tag and meta_tag.get("content"):
            meta_description = self._clean_text(meta_tag.get("content", ""))
        text = self._clean_text(soup.get_text(" ", strip=True))
        emails = self._extract_emails(text, soup)
        phones = self._extract_phones(text)
        social_links = self._extract_social_links(soup)
        technologies = self._extract_technologies(text, soup)
        return {
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "emails": emails,
            "phones": phones,
            "social_links": social_links,
            "technologies": technologies,
            "text": text,
        }

    def _request(self, url: str, *, timeout: int | None = None, headers: dict[str, str] | None = None) -> requests.Response:
        if hasattr(self, "_request_override"):
            return self._request_override(url, timeout=timeout or self.timeout, headers=headers or {})
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=timeout or self.timeout, headers=headers or {})
                response.raise_for_status()
                return response
            except requests.RequestException as exc:  # type: ignore[misc]
                if attempt == self.max_retries - 1:
                    raise AdapterError(f"Request failed for {url}: {exc}") from exc
                time.sleep(self.retry_delay * (attempt + 1))
        raise AdapterError(f"Unable to retrieve {url}")

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc.rstrip('/')}{parsed.path or '/'}"

    def _join_url(self, base_url: str, path: str) -> str:
        return urljoin(base_url, path)

    def _should_fetch(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"}

    def _extract_domain(self, url: str) -> str | None:
        parsed = urlparse(url)
        return parsed.netloc or None

    def _merge_pages(self, pages: list[dict[str, Any]]) -> dict[str, Any]:
        merged: dict[str, Any] = {
            "company_name": "",
            "industry": "Other",
            "emails": [],
            "phones": [],
            "social_links": [],
            "technologies": [],
            "meta_description": "",
        }
        for page in pages:
            if not merged["company_name"] and page.get("title"):
                merged["company_name"] = page["title"]
            merged["emails"].extend(page.get("emails", []))
            merged["phones"].extend(page.get("phones", []))
            merged["social_links"].extend(page.get("social_links", []))
            merged["technologies"].extend(page.get("technologies", []))
            if not merged["meta_description"] and page.get("meta_description"):
                merged["meta_description"] = page["meta_description"]
        merged["emails"] = self._unique(merged["emails"])
        merged["phones"] = [self._normalize_phone(phone) for phone in self._unique(merged["phones"])]
        merged["social_links"] = self._unique(merged["social_links"])
        merged["technologies"] = self._normalize_tech(self._unique(merged["technologies"]))
        return merged

    def _extract_emails(self, text: str, soup: BeautifulSoup | None = None) -> list[str]:
        emails = [email.lower() for email in self._unique(self.EMAIL_RE.findall(text))]
        if soup is not None:
            for anchor in soup.find_all("a", href=True):
                href = anchor.get("href", "")
                match = self.EMAIL_RE.search(href)
                if match:
                    emails.append(match.group(0).lower())
            for anchor in soup.find_all("a", href=True):
                href = anchor.get("href", "")
                if href.startswith("mailto:"):
                    address = href.split(":", 1)[1].split("?", 1)[0]
                    if address:
                        emails.append(address.lower())
        return self._unique(emails)

    def _extract_phones(self, text: str) -> list[str]:
        phones = []
        for match in self.PHONE_RE.findall(text):
            normalized = self._normalize_phone(match)
            if normalized:
                phones.append(normalized)
        return phones

    def _extract_social_links(self, soup: BeautifulSoup) -> list[str]:
        links = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if self.SOCIAL_RE.search(href):
                links.append(href)
        return self._unique(links)

    def _extract_technologies(self, text: str, soup: BeautifulSoup) -> list[str]:
        found = []
        lowered = text.lower()
        for tech in self.TECHNOLOGY_HINTS:
            if tech in lowered:
                found.append(tech)
        script_text = " ".join(script.get_text(" ", strip=True) for script in soup.find_all("script") if script.get_text(strip=True))
        if script_text.lower():
            for tech in self.TECHNOLOGY_HINTS:
                if tech in script_text.lower():
                    found.append(tech)
        return self._unique(found)

    def _normalize_phone(self, phone: str) -> str:
        digits = re.sub(r"\D", "", phone)
        if len(digits) == 10:
            return f"1{digits}"
        if len(digits) == 11 and digits.startswith("1"):
            return digits
        return digits

    def _normalize_tags(self, technologies: list[str], social_links: list[str]) -> list[str]:
        tags = [tech.lower() for tech in technologies]
        tags.extend(["social" for _ in social_links])
        return self._unique(tags)

    def _normalize_tech(self, technologies: list[str]) -> list[str]:
        return [tech.lower() for tech in technologies]

    def _unique(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                ordered.append(value)
        return ordered

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
