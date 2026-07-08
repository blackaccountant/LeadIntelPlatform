from __future__ import annotations

import requests

from adapters.opencorporates import OpenCorporatesAdapter


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.headers = {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

    def json(self) -> dict:
        return self._payload


def test_fetch_builds_leads_from_search_results(monkeypatch) -> None:
    adapter = OpenCorporatesAdapter(api_token="test-token", cache_ttl_seconds=60)

    payload = {
        "results": {
            "companies": [
                {
                    "company": {
                        "name": "Example Corp",
                        "jurisdiction_code": "us_ca",
                        "company_type": "Corporation",
                        "company_number": "12345",
                        "incorporation_date": "2020-01-01",
                        "registered_address_in_full": "1 Market St, San Francisco, CA 94105",
                    }
                }
            ],
            "page": 1,
            "per_page": 1,
            "total_pages": 1,
            "total_count": 1,
        }
    }

    monkeypatch.setattr(adapter, "_request", lambda *args, **kwargs: DummyResponse(payload))

    leads = adapter.fetch(company_name="Example Corp", jurisdiction="us_ca", location="San Francisco")

    assert len(leads) == 1
    lead = leads[0]
    assert lead.company is not None
    assert lead.company.name == "Example Corp"
    assert lead.company.industry == "Corporation"
    assert lead.contact is not None
    assert lead.source.startswith("opencorporates")


def test_fetch_paginates_and_caches(monkeypatch) -> None:
    adapter = OpenCorporatesAdapter(api_token="test-token", cache_ttl_seconds=60)
    responses = [
        DummyResponse({"results": {"companies": [{"company": {"name": "Alpha", "jurisdiction_code": "us_ca", "company_type": "LLC", "company_number": "1"}}], "page": 1, "per_page": 1, "total_pages": 2, "total_count": 2}}),
        DummyResponse({"results": {"companies": [{"company": {"name": "Beta", "jurisdiction_code": "us_ca", "company_type": "LLC", "company_number": "2"}}], "page": 2, "per_page": 1, "total_pages": 2, "total_count": 2}}),
    ]
    calls = []

    def fake_request(*args, **kwargs):
        calls.append(kwargs.get("params", {}))
        return responses.pop(0)

    monkeypatch.setattr(adapter, "_request", fake_request)

    first = adapter.fetch(company_name="Acme", jurisdiction="us_ca", location="San Francisco", page_limit=2)
    second = adapter.fetch(company_name="Acme", jurisdiction="us_ca", location="San Francisco", page_limit=2)

    assert len(first) == 2
    assert len(second) == 2
    assert len(calls) == 2
