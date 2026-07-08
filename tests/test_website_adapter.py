from __future__ import annotations

from adapters.website.adapter import WebsiteAdapter


class DummyResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code
        self.headers = {"content-type": "text/html; charset=utf-8"}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception("boom")


def test_fetch_extracts_company_and_contact_data(monkeypatch) -> None:
    adapter = WebsiteAdapter(cache_ttl_seconds=60)

    html = """
    <html>
      <head>
        <title>Example Company</title>
        <meta name="description" content="A software company" />
      </head>
      <body>
        <h1>Example Company</h1>
        <a href="https://www.linkedin.com/company/example">LinkedIn</a>
        <a href="https://twitter.com/example">Twitter</a>
        <a href="mailto:team@example.com">Email</a>
        <p>Call us at +1 (415) 555-0101</p>
        <script>window.__INITIAL_STATE__ = {"tech": ["Python", "Django"]};</script>
      </body>
    </html>
    """

    def fake_request(url: str, *, timeout: int, headers: dict | None = None) -> DummyResponse:
        return DummyResponse(html)

    monkeypatch.setattr(adapter, "_request_override", fake_request, raising=False)

    leads = adapter.fetch("https://example.com")
    assert len(leads) == 1
    lead = leads[0]
    assert lead.company is not None
    assert lead.company.name == "Example Company"
    assert lead.contact is not None
    assert lead.contact.email == "team@example.com"
    assert lead.contact.phone == "14155550101"
    assert "python" in lead.tags
