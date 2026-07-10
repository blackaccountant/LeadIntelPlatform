from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models import Lead


@dataclass(slots=True)
class QualificationResult:
    """Represents the outcome of applying lead qualification rules."""

    is_qualified: bool
    reason: str


class LeadQualificationService:
    """Apply a conservative set of heuristics for lead qualification."""

    GOVERNMENT_HINTS = ("government", "city of", "county", "state of", "school", "university", "police")
    CLOSED_HINTS = ("closed", "out of business", "bankrupt", "liquidated", "ceased")
    NON_BUSINESS_HINTS = ("nonprofit", "charity", "foundation", "church", "religious")

    def qualify(self, lead: Lead, *, seen_websites: set[str] | None = None, seen_phones: set[str] | None = None) -> QualificationResult:
        if lead.company is None or lead.contact is None:
            return QualificationResult(False, "missing_company_or_contact")

        company_name = (lead.company.name or "").lower()
        website = (lead.company.website or "").strip().lower()
        phone = (lead.contact.phone or "").strip()
        country = ""
        if lead.contact.address is not None:
            country = (lead.contact.address.country or "").strip().lower()
        if lead.company.headquarters is not None:
            country = (lead.company.headquarters.country or country).strip().lower()

        if country and country not in {"us", "united states", "usa"}:
            return QualificationResult(False, "outside_us")

        if not website:
            return QualificationResult(False, "no_website")

        if website.endswith((".gov", ".edu")):
            return QualificationResult(False, "government_or_educational")

        if any(hint in company_name for hint in self.GOVERNMENT_HINTS):
            return QualificationResult(False, "government")

        if any(hint in company_name for hint in self.NON_BUSINESS_HINTS):
            return QualificationResult(False, "non_business")

        if any(hint in company_name for hint in self.CLOSED_HINTS):
            return QualificationResult(False, "closed_business")

        if seen_websites is not None and website in seen_websites:
            return QualificationResult(False, "duplicate_website")

        if seen_phones is not None and phone and phone in seen_phones:
            return QualificationResult(False, "duplicate_phone")

        return QualificationResult(True, "qualified")
