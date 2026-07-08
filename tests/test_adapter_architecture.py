import pytest

from adapters.base import BaseAdapter
from adapters.business_directory import BusinessDirectoryAdapter
from models import Company, Contact, Lead
from pipeline import normalize_lead, route_lead, validate_lead
from services.lead_ingestion_service import LeadIngestionService


class DummyAdapter(BaseAdapter):
    def __init__(self, leads: list[Lead]) -> None:
        self._leads = leads

    def fetch(self, *args, **kwargs) -> list[Lead]:
        return self._leads


class RepositoryStub:
    def __init__(self) -> None:
        self.saved: list[Lead] = []

    def create_lead(self, lead: Lead, duplicate_rules: list[str] | None = None) -> Lead:
        self.saved.append(lead)
        return lead


def build_sample_lead() -> Lead:
    company = Company(name="Example Inc", website="https://example.com", industry="Software")
    contact = Contact(first_name="Ada", last_name="Lovelace", email="ada@example.com")
    return Lead(company=company, contact=contact, source="business_directory", confidence_score=0.8)


def test_base_adapter_requires_fetch_implementation() -> None:
    with pytest.raises(TypeError):
        BaseAdapter()  # type: ignore[abstract]


def test_business_directory_adapter_is_available() -> None:
    adapter = BusinessDirectoryAdapter(category="software", location="United States")
    assert adapter.category == "software"
    assert adapter.location == "United States"


def test_pipeline_helpers_normalize_and_route() -> None:
    lead = build_sample_lead()
    normalized = normalize_lead(lead)
    assert normalized.company.website == "https://example.com"
    assert route_lead(normalized) == "business_directory"
    validate_lead(normalized)


def test_ingestion_service_accepts_adapter() -> None:
    repository = RepositoryStub()
    service = LeadIngestionService(repository=repository)
    metrics = service.ingest(DummyAdapter([build_sample_lead()]), page_limit=1)
    assert metrics["leads_saved"] == 1
    assert metrics["duplicates_skipped"] == 0
