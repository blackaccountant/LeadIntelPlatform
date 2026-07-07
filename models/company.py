from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from models.address import Address
from models.enums import Industry

WEBSITE_REGEXP = re.compile(
    r"^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$",
    re.IGNORECASE,
)


@dataclass
class Company:
    """Represents a target company for a lead.

    The company model is built for both discovery and enrichment. It includes
    common company metadata and optional headquarters details.
    """

    name: str
    website: str | None = None
    domain: str | None = None
    industry: str | Industry | None = None
    employee_count: int | None = None
    headquarters: Address | None = None

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if self.website is not None:
            self.website = self.website.strip()
        if self.domain is not None:
            self.domain = self.domain.strip()
        if isinstance(self.industry, Industry):
            self.industry = self.industry
        elif self.industry is not None:
            self.industry = self.industry.strip()
        self.validate()

    def validate(self) -> None:
        """Validate company information."""
        if not self.name:
            raise ValueError("Company name must not be empty")
        if self.website and not WEBSITE_REGEXP.match(self.website):
            raise ValueError(f"Invalid website URL: {self.website}")
        if self.employee_count is not None and self.employee_count < 0:
            raise ValueError("employee_count must be a non-negative integer")

    def to_dict(self) -> dict[str, Any]:
        """Serialize company to JSON-safe dictionary."""
        return {
            "name": self.name,
            "website": self.website,
            "domain": self.domain,
            "industry": self.industry.value if isinstance(self.industry, Industry) else self.industry,
            "employee_count": self.employee_count,
            "headquarters": self.headquarters.to_dict() if self.headquarters else None,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Company:
        """Create a Company from serialized data."""
        return cls(
            name=raw.get("name", ""),
            website=raw.get("website"),
            domain=raw.get("domain"),
            industry=raw.get("industry"),
            employee_count=raw.get("employee_count"),
            headquarters=Address.from_dict(raw["headquarters"]) if isinstance(raw.get("headquarters"), dict) else None,
        )

    def __repr__(self) -> str:
        return (
            f"Company(name={self.name!r}, website={self.website!r}, "
            f"industry={self.industry!r}, employee_count={self.employee_count!r})"
        )
