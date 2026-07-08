from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

from models import Lead
from database.repository import LeadRepository
from pipeline import normalize_lead, route_lead, validate_lead


class LeadIngestionService:
    """Orchestrates adapter-driven ingestion, validation, deduplication, persistence, and export."""

    def __init__(
        self,
        repository: LeadRepository,
        export_path: str | Path | None = None,
        duplicate_rules: list[str] | None = None,
    ) -> None:
        self._repository = repository
        self._logger = logging.getLogger(self.__class__.__name__)
        self._export_path = Path(export_path) if export_path is not None else None
        self._duplicate_rules = duplicate_rules

    def ingest(self, adapter: Any, **scrape_kwargs: Any) -> dict[str, int]:
        """Run an adapter, normalize and validate leads, persist unique leads, and export saved leads."""
        self._logger.info("Starting lead ingestion")
        discovered_leads: list[Lead] = []
        pages_scraped = 0

        if hasattr(adapter, "__enter__") and hasattr(adapter, "__exit__"):
            with adapter:
                discovered_leads = adapter.fetch(**scrape_kwargs)
                pages_scraped = getattr(adapter, "pages_scraped", 0) or 0
        else:
            discovered_leads = adapter.fetch(**scrape_kwargs)
            pages_scraped = getattr(adapter, "pages_scraped", 0) or 0
        self._logger.info(
            "Adapter completed",
            extra={"pages_scraped": pages_scraped, "leads_discovered": len(discovered_leads)},
        )

        duplicates_skipped = 0
        saved_leads: list[Lead] = []

        for lead in discovered_leads:
            try:
                normalized = normalize_lead(lead)
                validate_lead(normalized)
                route = route_lead(normalized)
                self._logger.debug("Routed lead", extra={"route": route, "source": normalized.source})
            except Exception as exc:
                self._logger.warning(
                    "Invalid lead skipped",
                    exc_info=exc,
                    extra={"lead_id": getattr(lead, "id", None), "company": getattr(lead.company, "name", None)},
                )
                continue

            try:
                saved = self._repository.create_lead(normalized, duplicate_rules=self._duplicate_rules)
                saved_leads.append(saved)
            except ValueError:
                duplicates_skipped += 1
            except Exception as exc:
                self._logger.error(
                    "Failed to save lead",
                    exc_info=exc,
                    extra={"company": normalized.company.name, "source": normalized.source},
                )

        if self._export_path is not None and saved_leads:
            self._export_to_csv(saved_leads, self._export_path)

        metrics = {
            "pages_scraped": pages_scraped,
            "leads_discovered": len(discovered_leads),
            "duplicates_skipped": duplicates_skipped,
            "leads_saved": len(saved_leads),
        }
        self._logger.info("Lead ingestion completed", extra=metrics)
        return metrics

    def _export_to_csv(self, leads: list[Lead], destination: Path) -> None:
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
            "created_at",
            "updated_at",
            "address_city",
            "address_region",
            "address_postal_code",
            "address_country",
        ]

        with destination.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                writer.writerow(self._lead_to_csv_row(lead))

        self._logger.info("Exported saved leads to CSV", extra={"path": str(destination), "count": len(leads)})

    def _lead_to_csv_row(self, lead: Lead) -> dict[str, str]:
        return {
            "id": str(lead.id),
            "company_name": lead.company.name,
            "company_website": lead.company.website or "",
            "company_domain": lead.company.domain or "",
            "company_industry": lead.company.industry.value if hasattr(lead.company.industry, "value") else str(lead.company.industry),
            "contact_phone": lead.contact.phone or "",
            "contact_email": lead.contact.email or "",
            "source": lead.source,
            "confidence_score": str(lead.confidence_score),
            "status": lead.status.value if hasattr(lead.status, "value") else str(lead.status),
            "tags": ",".join(lead.tags),
            "notes": " | ".join(lead.notes),
            "created_at": lead.created_at.isoformat(),
            "updated_at": lead.updated_at.isoformat(),
            "address_city": lead.contact.address.city if lead.contact.address else "",
            "address_region": lead.contact.address.region if lead.contact.address else "",
            "address_postal_code": lead.contact.address.postal_code if lead.contact.address else "",
            "address_country": lead.contact.address.country if lead.contact.address else "",
        }
