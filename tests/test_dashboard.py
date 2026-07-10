from __future__ import annotations

from services.dashboard_service import DashboardSummary, render_dashboard_html
from models import Company, Contact, Lead


def build_sample_lead(name: str, website: str, email: str, status: str = "new") -> Lead:
    company = Company(name=name, website=website, industry="Software")
    contact = Contact(first_name="Ada", last_name="Lovelace", email=email)
    return Lead(company=company, contact=contact, source="campaign", status=status, confidence_score=0.9)


def test_render_dashboard_html_includes_summary_and_leads() -> None:
    leads = [
        build_sample_lead("Northwind Labs", "https://northwind.example", "ada@northwind.example"),
        build_sample_lead("Acme Plumbing", "https://acme.example", "team@acme.example"),
    ]
    summary = DashboardSummary(total_leads=2, qualified_leads=1, pending_leads=1, exported_leads=0)

    html = render_dashboard_html(leads, summary)

    assert "Lead Intelligence Dashboard" in html
    assert "2" in html
    assert "Northwind Labs" in html
    assert "Acme Plumbing" in html
