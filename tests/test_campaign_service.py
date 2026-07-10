from __future__ import annotations

from adapters.base import BaseAdapter
from models import Company, Contact, Lead
from services.campaign_service import CampaignCriteria, CampaignManager


class DummyAdapter(BaseAdapter):
    def __init__(self, leads: list[Lead]) -> None:
        super().__init__()
        self._leads = leads

    def fetch(self, *args, **kwargs) -> list[Lead]:
        return list(self._leads)


class RepositoryStub:
    def __init__(self) -> None:
        self.saved: list[Lead] = []

    def create_lead(self, lead: Lead, duplicate_rules: list[str] | None = None) -> Lead:
        self.saved.append(lead)
        return lead


def build_sample_lead(name: str, website: str, phone: str | None = None) -> Lead:
    company = Company(name=name, website=website, industry="Software")
    contact = Contact(first_name="Ada", last_name="Lovelace", email="ada@example.com", phone=phone)
    return Lead(company=company, contact=contact, source="test_adapter", confidence_score=0.8)


def test_campaign_manager_filters_and_saves_leads() -> None:
    repository = RepositoryStub()
    manager = CampaignManager(repository)  # type: ignore[arg-type]
    criteria = CampaignCriteria(country="US", industry="plumber", limit=5)
    adapters = [DummyAdapter([build_sample_lead("Apex Plumbing", "https://apexplumbing.com", "+12125550101")])]

    summary = manager.run(adapters, criteria)

    assert summary.discovered == 1
    assert summary.qualified == 1
    assert summary.saved == 1
    assert repository.saved[0].company.name == "Apex Plumbing"
