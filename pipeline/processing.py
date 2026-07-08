from __future__ import annotations

from models import Lead


def validate_lead(lead: Lead) -> Lead:
    """Validate a lead and raise if it is structurally invalid."""
    lead.validate()
    return lead


def normalize_lead(lead: Lead) -> Lead:
    """Normalize a lead's core fields before routing or persistence."""
    if lead.company is not None:
        lead.company.website = (lead.company.website or "").strip() or None
        lead.company.domain = (lead.company.domain or "").strip() or None
    if lead.contact is not None:
        lead.contact.phone = (lead.contact.phone or "").strip() or None
        lead.contact.email = (lead.contact.email or "").strip() or None
    return lead


def route_lead(lead: Lead) -> str:
    """Infer a routing target from the lead's source metadata."""
    source = (lead.source or "").lower()
    if "opencorporates" in source:
        return "opencorporates"
    if "business_directory" in source:
        return "business_directory"
    return "default"
