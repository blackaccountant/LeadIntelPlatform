from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from models.company import Company
from models.contact import Contact
from models.enums import Industry, LeadStatus, parse_enum


def _normalize_text_list(values: list[str] | None) -> list[str]:
    return [value.strip() for value in values or [] if value and value.strip()]


@dataclass
class Lead:
    """Core lead domain model representing a discovered or enriched lead."""

    id: UUID = field(default_factory=uuid4)
    company: Company | None = None
    contact: Contact | None = None
    source: str = ""
    industry: str | Industry = Industry.OTHER
    confidence_score: float = 0.0
    status: LeadStatus = LeadStatus.NEW
    tags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self.source = self.source.strip()
        if isinstance(self.industry, Industry):
            self.industry = self.industry
        elif isinstance(self.industry, str):
            self.industry = self.industry.strip() or Industry.OTHER
        self.tags = _normalize_text_list(self.tags)
        self.notes = _normalize_text_list(self.notes)
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        if self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)
        self.validate()

    def validate(self) -> None:
        """Validate lead consistency and required core references."""
        if self.company is None:
            raise ValueError("Lead.company must be provided")
        if self.contact is None:
            raise ValueError("Lead.contact must be provided")
        if not self.source:
            raise ValueError("Lead.source must not be empty")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        if self.created_at > self.updated_at:
            raise ValueError("created_at must not be later than updated_at")
        if isinstance(self.status, LeadStatus):
            self.status = self.status
        else:
            self.status = parse_enum(LeadStatus, self.status)
        if isinstance(self.industry, Industry):
            self.industry = self.industry
        elif isinstance(self.industry, str):
            self.industry = self.industry.strip() or Industry.OTHER

    def to_dict(self) -> dict[str, Any]:
        """Serialize the Lead to a JSON-safe dictionary."""
        return {
            "id": str(self.id),
            "company": self.company.to_dict(),
            "contact": self.contact.to_dict(),
            "source": self.source,
            "industry": self.industry.value if isinstance(self.industry, Industry) else self.industry,
            "confidence_score": self.confidence_score,
            "status": self.status.value,
            "tags": self.tags,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Lead:
        """Create a Lead from serialized data."""
        created_at = raw.get("created_at")
        updated_at = raw.get("updated_at")
        return cls(
            id=UUID(raw["id"]) if raw.get("id") else uuid4(),
            company=Company.from_dict(raw["company"]),
            contact=Contact.from_dict(raw["contact"]),
            source=raw.get("source", ""),
            industry=raw.get("industry", Industry.OTHER.value),
            confidence_score=float(raw.get("confidence_score", 0.0)),
            status=raw.get("status", LeadStatus.NEW.value),
            tags=list(raw.get("tags", [])),
            notes=list(raw.get("notes", [])),
            created_at=datetime.fromisoformat(created_at) if isinstance(created_at, str) else datetime.now(timezone.utc),
            updated_at=datetime.fromisoformat(updated_at) if isinstance(updated_at, str) else datetime.now(timezone.utc),
        )

    def __repr__(self) -> str:
        return (
            f"Lead(id={self.id!r}, company={self.company.name!r}, contact={self.contact.first_name!r} "
            f"{self.contact.last_name!r}, status={self.status.value!r}, confidence_score={self.confidence_score!r})"
        )
