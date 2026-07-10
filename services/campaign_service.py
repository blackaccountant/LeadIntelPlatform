from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from adapters.base import BaseAdapter
from database.repository import LeadRepository
from database.session import DatabaseSessionManager
from models import Company, Contact, Lead
from services.lead_ingestion_service import LeadIngestionService
from services.qualification_service import LeadQualificationService


@dataclass(slots=True)
class CampaignCriteria:
    """Input criteria for a discovery campaign."""

    country: str | None = None
    state: str | None = None
    city: str | None = None
    industry: str | None = None
    keyword: str | None = None
    limit: int = 100
    ai: bool = False
    dry_run: bool = False
    export: str | None = None


@dataclass(slots=True)
class CampaignSummary:
    """Summary of what a campaign processed."""

    discovered: int = 0
    qualified: int = 0
    rejected: int = 0
    saved: int = 0
    output_path: str | None = None


class CampaignManager:
    """Orchestrate adapter-driven discovery, qualification, scoring, and export."""

    def __init__(self, repository: LeadRepository, *, logger: logging.Logger | None = None) -> None:
        self._repository = repository
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._qualification_service = LeadQualificationService()
        self._ingestion_service = LeadIngestionService(repository=repository)

    def run(self, adapters: list[BaseAdapter], criteria: CampaignCriteria) -> CampaignSummary:
        seen_websites: set[str] = set()
        seen_phones: set[str] = set()
        accepted: list[Lead] = []
        rejected = 0
        discovered = 0

        for adapter in adapters:
            self._logger.info("Running adapter", extra={"adapter": adapter.__class__.__name__})
            discovered_leads = adapter.fetch(
                country=criteria.country,
                state=criteria.state,
                city=criteria.city,
                industry=criteria.industry,
                keyword=criteria.keyword,
                page_limit=criteria.limit,
            )
            discovered += len(discovered_leads)
            for lead in discovered_leads:
                qualification = self._qualification_service.qualify(lead, seen_websites=seen_websites, seen_phones=seen_phones)
                if not qualification.is_qualified:
                    rejected += 1
                    self._logger.info("Rejected lead", extra={"reason": qualification.reason, "company": getattr(lead.company, "name", None)})
                    continue
                website = (lead.company.website or "").strip().lower()
                phone = (lead.contact.phone or "").strip() if lead.contact is not None else ""
                if website:
                    seen_websites.add(website)
                if phone:
                    seen_phones.add(phone)
                if not criteria.dry_run:
                    try:
                        saved = self._repository.create_lead(lead)
                        accepted.append(saved)
                    except ValueError:
                        rejected += 1
                else:
                    accepted.append(lead)

        summary = CampaignSummary(discovered=discovered, qualified=len(accepted), rejected=rejected, saved=len(accepted), output_path=None)
        if criteria.export:
            export_path = Path(criteria.export)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            self._export_csv(accepted, export_path)
            summary.output_path = str(export_path)
        return summary

    def _export_csv(self, leads: list[Lead], destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "id",
            "company_name",
            "company_website",
            "company_domain",
            "company_industry",
            "contact_phone",
            "contact_email",
            "source",
            "confidence_score",
            "status",
            "tags",
            "notes",
        ]
        with destination.open("w", newline="", encoding="utf-8") as csv_file:
            writer = __import__("csv").DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                writer.writerow({
                    "id": str(lead.id),
                    "company_name": lead.company.name if lead.company else "",
                    "company_website": lead.company.website or "" if lead.company else "",
                    "company_domain": lead.company.domain or "" if lead.company else "",
                    "company_industry": lead.company.industry.value if hasattr(lead.company.industry, "value") else str(lead.company.industry) if lead.company else "",
                    "contact_phone": lead.contact.phone or "" if lead.contact else "",
                    "contact_email": lead.contact.email or "" if lead.contact else "",
                    "source": lead.source,
                    "confidence_score": str(lead.confidence_score),
                    "status": lead.status.value if hasattr(lead.status, "value") else str(lead.status),
                    "tags": ",".join(lead.tags),
                    "notes": " | ".join(lead.notes),
                })
