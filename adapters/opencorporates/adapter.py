from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from dotenv import load_dotenv

from adapters.base import AdapterError, BaseAdapter
from models import Address, Company, Contact, Lead

load_dotenv()


class OpenCorporatesAdapter(BaseAdapter):
    """Adapter for the official OpenCorporates API."""

    API_BASE_URL = "https://api.opencorporates.com/v0.4"

    def __init__(
        self,
        *,
        api_token: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        cache_ttl_seconds: int = 300,
        session: requests.Session | None = None,
    ) -> None:
        super().__init__()
        self.api_token = api_token or os.getenv("OPENCORPORATES_API_TOKEN")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache_ttl_seconds = cache_ttl_seconds
        self.session = session or requests.Session()
        self._cache: dict[tuple[tuple[str, str], tuple[tuple[str, str], ...]], tuple[float, list[Lead]]] = {}

    def fetch(self, *args: Any, **kwargs: Any) -> list[Lead]:
        """Search companies by name, jurisdiction, and location, then convert to Lead objects."""
        company_name = kwargs.get("company_name") or kwargs.get("name") or ""
        jurisdiction = kwargs.get("jurisdiction") or ""
        location = kwargs.get("location") or ""
        page_limit = kwargs.get("page_limit", 1)

        cache_key = (
            ("company_name", str(company_name)),
            (("jurisdiction", str(jurisdiction)), ("location", str(location))),
        )
        cached = self._cache.get(cache_key)
        if cached is not None and (time.monotonic() - cached[0]) < self.cache_ttl_seconds:
            return list(cached[1])

        leads: list[Lead] = []
        page = 1
        while page <= page_limit:
            params = self._build_params(company_name=company_name, jurisdiction=jurisdiction, location=location, page=page)
            payload = self._request("/companies/search", params=params)
            page_results = self._extract_companies(payload)
            leads.extend(page_results)
            if hasattr(payload, "json"):
                payload = payload.json()
            page_info = payload.get("results", {}) if isinstance(payload, dict) else {}
            total_pages = int(page_info.get("total_pages", 0) or 0)
            if total_pages <= page or not page_results:
                break
            page += 1

        self._cache[cache_key] = (time.monotonic(), list(leads))
        return leads

    def _build_params(self, *, company_name: str, jurisdiction: str, location: str, page: int) -> dict[str, str | int]:
        params: dict[str, str | int] = {"q": company_name, "page": page}
        if jurisdiction:
            params["jurisdiction_code"] = jurisdiction
        if location:
            params["location"] = location
        return params

    def _request(self, path: str, *, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_token:
            raise AdapterError("OPENCORPORATES_API_TOKEN is not configured")

        url = f"{self.API_BASE_URL}{path}"
        headers = {"Authorization": f"Token {self.api_token}"}
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:  # type: ignore[misc]
                last_error = exc
                if attempt == self.max_retries - 1:
                    raise AdapterError(f"OpenCorporates request failed: {exc}") from exc
                time.sleep(self.retry_delay * (attempt + 1))
        raise AdapterError("OpenCorporates request exhausted retries") from last_error

    def _extract_companies(self, payload: dict[str, Any] | Any) -> list[Lead]:
        if hasattr(payload, "json"):
            payload = payload.json()
        results = payload.get("results", {}) if isinstance(payload, dict) else {}
        companies = results.get("companies", [])
        leads: list[Lead] = []
        for item in companies:
            company_data = item.get("company") or {}
            company_name = str(company_data.get("name") or "").strip()
            if not company_name:
                continue
            lead = self._to_lead(company_data)
            if lead is not None:
                leads.append(lead)
        return leads

    def _to_lead(self, company_data: dict[str, Any]) -> Lead | None:
        company_name = str(company_data.get("name") or "").strip()
        if not company_name:
            return None

        address_text = str(company_data.get("registered_address_in_full") or "").strip()
        address = self._build_address(address_text)
        company = Company(
            name=company_name,
            website=None,
            domain=None,
            industry=str(company_data.get("company_type") or "").strip() or "Unknown",
            headquarters=address,
        )
        contact = Contact(
            first_name=company_name,
            last_name="",
            phone=None,
            email=None,
            address=address,
        )
        return Lead(
            company=company,
            contact=contact,
            source=f"opencorporates:{company_data.get('jurisdiction_code', 'unknown')}",
            industry=company.industry,
            confidence_score=0.75,
            status="new",
            tags=["opencorporates"],
            notes=[f"jurisdiction={company_data.get('jurisdiction_code', '')}"],
        )

    def _build_address(self, address_text: str) -> Address | None:
        if not address_text:
            return None
        parts = [part.strip() for part in address_text.split(",") if part.strip()]
        if not parts:
            return None
        street_address = parts[0] if len(parts) >= 1 else ""
        city = parts[1] if len(parts) >= 2 else ""
        region = parts[2] if len(parts) >= 3 else ""
        postal_code = parts[-1] if len(parts) >= 4 else "00000"
        return Address(
            street_address=street_address,
            city=city,
            region=region,
            postal_code=postal_code,
            country="United States",
        )
