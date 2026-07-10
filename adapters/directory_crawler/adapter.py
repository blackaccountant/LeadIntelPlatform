"""Generic business-directory crawler adapter.

Crawls any paginated business-directory website (allbiz.com, yelp.com,
yellowpages.com, bizapedia.com, etc.) and extracts company leads using
a hierarchy of heuristic strategies:

1. JSON-LD / schema.org LocalBusiness / Organization structured data
2. meta / microdata itemprop attributes
3. ``tel:`` and ``mailto:`` href links
4. Regex fallbacks for phone numbers and email addresses
5. Pagination via common ``rel="next"`` links or URL pattern incrementing
"""

from __future__ import annotations

import re
import time
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode

import requests
from bs4 import BeautifulSoup

from adapters.base import AdapterError, BaseAdapter
from models import Address, Company, Contact, Lead


_PHONE_RE = re.compile(r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
_EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE)
_DOMAIN_RE = re.compile(r"^(?:https?://)?(?:www\.)?([^/]+)", re.IGNORECASE)

# Candidate CSS selectors tried in order – first match wins
_LISTING_CANDIDATES = [
    # Schema.org itemtype
    "[itemtype*='LocalBusiness']",
    "[itemtype*='Organization']",
    # Common class fragments
    "[class*='result']",
    "[class*='listing']",
    "[class*='business']",
    "[class*='company']",
    "[class*='card']",
    "[class*='entry']",
    # Structural fallbacks
    "article",
    "li",
]

_NAME_CANDIDATES = [
    "h1", "h2", "h3",
    "[itemprop='name']",
    "[class*='name']",
    "[class*='title']",
    "a[href*='/business']",
    "a[href*='/company']",
    "a[href*='/biz']",
]

_PHONE_CANDIDATES = [
    "a[href^='tel:']",
    "[itemprop='telephone']",
    "[class*='phone']",
    "[class*='tel']",
    "[class*='call']",
]

_ADDRESS_CANDIDATES = [
    "address",
    "[itemprop='address']",
    "[class*='address']",
    "[class*='location']",
    "[class*='addr']",
]

_WEBSITE_CANDIDATES = [
    "[itemprop='url']",
    "a[class*='website']",
    "a[class*='web']",
    "a[rel*='noopener']",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class DirectoryCrawlerAdapter(BaseAdapter):
    """Crawl any business-directory listing page and extract Lead objects."""

    def __init__(
        self,
        *,
        timeout: int = 20,
        max_retries: int = 3,
        retry_delay: float = 1.5,
        rate_limit_delay: float = 1.0,
        session: requests.Session | None = None,
    ) -> None:
        super().__init__()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self._session = session or requests.Session()
        self._session.headers.update(_HEADERS)

    # ------------------------------------------------------------------ #
    # Public interface                                                      #
    # ------------------------------------------------------------------ #

    def fetch(self, *args: Any, **kwargs: Any) -> list[Lead]:
        """Crawl a directory URL and return discovered leads.

        Keyword args:
            url (str): The listing / search-results page to crawl.
            page_limit (int): Max pages to follow. Default 3.
            keyword (str): Injected into URL ?q= / ?keyword= if provided.
            location (str): Injected into URL ?l= / ?location= if provided.
        """
        url: str = kwargs.get("url") or (args[0] if args else "")
        if not url:
            raise AdapterError("A directory URL is required")

        # Normalise
        if not url.startswith("http"):
            url = "https://" + url

        page_limit: int = int(kwargs.get("page_limit", 3))
        keyword: str = kwargs.get("keyword") or kwargs.get("q") or ""
        location: str = kwargs.get("location") or kwargs.get("l") or ""

        # Inject search params if the URL looks like a homepage
        start_url = self._inject_search_params(url, keyword=keyword, location=location)

        leads: list[Lead] = []
        visited: set[str] = set()
        current_url: str = start_url
        page = 0

        while current_url and page < page_limit:
            if current_url in visited:
                break
            visited.add(current_url)
            self._logger.info("Crawling directory page", extra={"url": current_url, "page": page + 1})

            html = self._get_html(current_url)
            if html is None:
                break

            soup = BeautifulSoup(html, "html.parser")

            # Try JSON-LD first (richest source)
            json_leads = self._extract_json_ld(soup, current_url)
            if json_leads:
                leads.extend(json_leads)
            else:
                # Fall back to heuristic DOM extraction
                dom_leads = self._extract_from_dom(soup, current_url)
                leads.extend(dom_leads)

            page += 1
            next_url = self._find_next_page(soup, current_url, page)
            current_url = next_url or ""
            if current_url:
                time.sleep(self.rate_limit_delay)

        # De-duplicate by phone / name
        leads = self._deduplicate(leads)
        self._logger.info("Directory crawl complete", extra={"leads": len(leads), "pages": page})
        return leads

    # ------------------------------------------------------------------ #
    # JSON-LD / Schema.org                                                 #
    # ------------------------------------------------------------------ #

    def _extract_json_ld(self, soup: BeautifulSoup, page_url: str) -> list[Lead]:
        import json
        leads: list[Lead] = []
        for tag in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(tag.string or "")
            except Exception:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                types = item.get("@type", "")
                if isinstance(types, list):
                    types = " ".join(types)
                if not any(t in types for t in ("LocalBusiness", "Organization", "Store", "Restaurant", "MedicalBusiness")):
                    continue
                lead = self._lead_from_schema(item, page_url)
                if lead:
                    leads.append(lead)
        return leads

    def _lead_from_schema(self, item: dict[str, Any], page_url: str) -> Lead | None:
        name: str = item.get("name", "").strip()
        if not name:
            return None

        phone = self._schema_telephone(item)
        email = item.get("email", "").strip() or None
        website = item.get("url", "").strip() or None
        industry = self._schema_category(item)
        address = self._schema_address(item)

        company = Company(
            name=name,
            website=website,
            domain=self._extract_domain(website) if website else None,
            industry=industry,
            headquarters=address,
        )
        contact = Contact(
            first_name="Business",
            last_name="Contact",
            email=email,
            phone=phone,
            title="Primary Contact",
        )
        return Lead(
            company=company,
            contact=contact,
            source=page_url,
            industry=industry,
            confidence_score=0.75,
            status="new",
            tags=[industry] if industry else [],
            notes=[item.get("description", "")[:200]] if item.get("description") else [],
        )

    def _schema_telephone(self, item: dict[str, Any]) -> str | None:
        tel = item.get("telephone", "")
        if isinstance(tel, list):
            tel = tel[0] if tel else ""
        return tel.strip() or None

    def _schema_category(self, item: dict[str, Any]) -> str:
        for key in ("@type", "category", "servesCuisine", "additionalType"):
            val = item.get(key, "")
            if isinstance(val, list):
                val = val[-1] if val else ""
            if val and val not in ("LocalBusiness", "Organization"):
                return str(val).strip()
        return ""

    def _schema_address(self, item: dict[str, Any]) -> Address | None:
        addr = item.get("address", {})
        if isinstance(addr, str):
            return Address(street_address=addr, city="", region="", postal_code="", country="US")
        if not isinstance(addr, dict):
            return None
        return Address(
            street_address=addr.get("streetAddress", ""),
            city=addr.get("addressLocality", ""),
            region=addr.get("addressRegion", ""),
            postal_code=addr.get("postalCode", ""),
            country=addr.get("addressCountry", "US"),
        )

    # ------------------------------------------------------------------ #
    # DOM heuristic extraction                                             #
    # ------------------------------------------------------------------ #

    def _extract_from_dom(self, soup: BeautifulSoup, page_url: str) -> list[Lead]:
        """Find listing elements using candidate selectors and extract leads."""
        listing_els: list[Any] = []
        for sel in _LISTING_CANDIDATES:
            try:
                els = soup.select(sel)
                if len(els) >= 2:  # need at least 2 to be a real listing block
                    listing_els = els
                    break
            except Exception:
                continue

        if not listing_els:
            # Whole page as single lead (single business profile page)
            return self._extract_single_business(soup, page_url)

        leads: list[Lead] = []
        for el in listing_els[:50]:  # cap per page
            lead = self._extract_one_listing(el, page_url)
            if lead:
                leads.append(lead)
        return leads

    def _extract_one_listing(self, el: Any, page_url: str) -> Lead | None:
        name = self._pick_text(el, _NAME_CANDIDATES)
        if not name or len(name) < 2:
            return None

        phone = self._extract_phone_from_el(el)
        email = self._extract_email_from_el(el)
        website = self._extract_website_from_el(el, page_url)
        address_text = self._pick_text(el, _ADDRESS_CANDIDATES)
        industry = self._guess_industry(el)

        address = self._parse_address_text(address_text) if address_text else None
        company = Company(
            name=name,
            website=website,
            domain=self._extract_domain(website) if website else None,
            industry=industry,
            headquarters=address,
        )
        contact = Contact(
            first_name="Business",
            last_name="Contact",
            email=email,
            phone=phone,
            title="Primary Contact",
        )
        return Lead(
            company=company,
            contact=contact,
            source=page_url,
            industry=industry,
            confidence_score=0.6,
            status="new",
            tags=[industry] if industry else [],
            notes=[],
        )

    def _extract_single_business(self, soup: BeautifulSoup, page_url: str) -> list[Lead]:
        """Handle a single business profile page (e.g. allbiz.com/business/...)."""
        name = ""
        for tag in ("h1", "h2"):
            el = soup.find(tag)
            if el:
                name = el.get_text(strip=True)
                break
        if not name:
            return []

        phone = self._extract_phone_from_el(soup)
        email = self._extract_email_from_el(soup)
        website = self._extract_website_from_el(soup, page_url)
        address_text = self._pick_text(soup, _ADDRESS_CANDIDATES)
        industry = self._guess_industry(soup)
        address = self._parse_address_text(address_text) if address_text else None

        company = Company(
            name=name,
            website=website,
            domain=self._extract_domain(website) if website else None,
            industry=industry,
            headquarters=address,
        )
        contact = Contact(
            first_name="Business",
            last_name="Contact",
            email=email,
            phone=phone,
            title="Primary Contact",
        )
        return [Lead(
            company=company,
            contact=contact,
            source=page_url,
            industry=industry,
            confidence_score=0.7,
            status="new",
            tags=[industry] if industry else [],
            notes=[],
        )]

    # ------------------------------------------------------------------ #
    # Extraction helpers                                                   #
    # ------------------------------------------------------------------ #

    def _pick_text(self, el: Any, selectors: list[str]) -> str:
        for sel in selectors:
            try:
                found = el.select_one(sel)
                if found:
                    return found.get_text(strip=True)
            except Exception:
                continue
        return ""

    def _extract_phone_from_el(self, el: Any) -> str | None:
        # 1. tel: href
        for sel in _PHONE_CANDIDATES:
            try:
                tag = el.select_one(sel)
                if tag:
                    href = tag.get("href", "")
                    if href.startswith("tel:"):
                        return href[4:].strip()
                    text = tag.get_text(strip=True)
                    if text:
                        return text
            except Exception:
                continue
        # 2. regex on full text
        text = el.get_text(" ", strip=True) if hasattr(el, "get_text") else str(el)
        match = _PHONE_RE.search(text)
        return match.group().strip() if match else None

    def _extract_email_from_el(self, el: Any) -> str | None:
        try:
            tag = el.select_one("a[href^='mailto:']")
            if tag:
                return tag["href"][7:].split("?")[0].strip()
        except Exception:
            pass
        text = el.get_text(" ", strip=True) if hasattr(el, "get_text") else str(el)
        match = _EMAIL_RE.search(text)
        return match.group() if match else None

    def _extract_website_from_el(self, el: Any, page_url: str) -> str | None:
        page_host = urlparse(page_url).netloc.lower().lstrip("www.")
        for sel in _WEBSITE_CANDIDATES:
            try:
                tag = el.select_one(sel)
                if tag:
                    href = tag.get("href", "").strip()
                    if href and href.startswith("http"):
                        host = urlparse(href).netloc.lower().lstrip("www.")
                        if host and host != page_host:
                            return href
            except Exception:
                continue
        # Any external link that isn't the directory itself
        try:
            for a in el.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("http"):
                    host = urlparse(href).netloc.lower().lstrip("www.")
                    if host and host != page_host:
                        return href
        except Exception:
            pass
        return None

    def _guess_industry(self, el: Any) -> str:
        for sel in ["[class*='category']", "[class*='industry']", "[class*='type']", "[class*='tag']"]:
            try:
                found = el.select_one(sel)
                if found:
                    text = found.get_text(strip=True)
                    if text and len(text) < 60:
                        return text
            except Exception:
                continue
        return ""

    def _parse_address_text(self, raw: str) -> Address:
        parts = [p.strip() for p in re.split(r"[,\n]", raw) if p.strip()]
        if len(parts) >= 3:
            return Address(
                street_address=parts[0],
                city=parts[-3] if len(parts) >= 3 else "",
                region=parts[-2] if len(parts) >= 2 else "",
                postal_code=parts[-1].split()[0] if parts[-1] else "",
                country="US",
            )
        return Address(street_address=raw[:100], city="", region="", postal_code="", country="US")

    # ------------------------------------------------------------------ #
    # Pagination                                                           #
    # ------------------------------------------------------------------ #

    def _find_next_page(self, soup: BeautifulSoup, current_url: str, current_page: int) -> str | None:
        # 1. rel="next"
        rel_next = soup.find("a", rel="next") or soup.find("link", rel="next")
        if rel_next and rel_next.get("href"):
            return urljoin(current_url, rel_next["href"])

        # 2. Common pagination text / class patterns
        for sel in ["a[class*='next']", "a[class*='Next']", "[class*='pagination'] a[href]"]:
            try:
                tags = soup.select(sel)
                for tag in tags:
                    text = tag.get_text(strip=True).lower()
                    href = tag.get("href", "")
                    if ("next" in text or "›" in text or "»" in text) and href:
                        return urljoin(current_url, href)
            except Exception:
                continue

        # 3. Increment page/p param
        parsed = urlparse(current_url)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        for key in ("page", "p", "pg", "start", "offset"):
            if key in qs:
                try:
                    val = int(qs[key][0])
                    qs[key] = [str(val + 1)]
                    new_qs = urlencode(qs, doseq=True)
                    return urlunparse(parsed._replace(query=new_qs))
                except (ValueError, IndexError):
                    continue

        return None

    # ------------------------------------------------------------------ #
    # HTTP                                                                 #
    # ------------------------------------------------------------------ #

    def _get_html(self, url: str) -> str | None:
        for attempt in range(self.max_retries):
            try:
                resp = self._session.get(url, timeout=self.timeout, allow_redirects=True)
                resp.raise_for_status()
                return resp.text
            except requests.exceptions.HTTPError as exc:
                self._logger.warning("HTTP error fetching page", extra={"url": url, "status": exc.response.status_code if exc.response else "?"})
                if exc.response is not None and exc.response.status_code in (401, 403, 404):
                    return None
                time.sleep(self.retry_delay * (attempt + 1))
            except Exception as exc:
                self._logger.warning("Error fetching page", extra={"url": url, "error": str(exc)})
                time.sleep(self.retry_delay * (attempt + 1))
        return None

    # ------------------------------------------------------------------ #
    # Utilities                                                            #
    # ------------------------------------------------------------------ #

    def _inject_search_params(self, url: str, keyword: str = "", location: str = "") -> str:
        """Add search params to a homepage URL if it doesn't already have a path."""
        parsed = urlparse(url)
        if parsed.path not in ("", "/") or not (keyword or location):
            return url
        qs: dict[str, str] = {}
        if keyword:
            qs["q"] = keyword
        if location:
            qs["l"] = location
        new_qs = urlencode(qs)
        return urlunparse(parsed._replace(query=new_qs))

    def _extract_domain(self, url: str | None) -> str | None:
        if not url:
            return None
        m = _DOMAIN_RE.match(url)
        return m.group(1) if m else None

    def _deduplicate(self, leads: list[Lead]) -> list[Lead]:
        seen_phones: set[str] = set()
        seen_names: set[str] = set()
        out: list[Lead] = []
        for lead in leads:
            phone = (lead.contact.phone or "").strip()
            name = (lead.company.name or "").strip().lower()
            if (phone and phone in seen_phones) or (name and name in seen_names):
                continue
            if phone:
                seen_phones.add(phone)
            if name:
                seen_names.add(name)
            out.append(lead)
        return out
