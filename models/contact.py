from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from models.address import Address

EMAIL_REGEXP = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_REGEXP = re.compile(
    r"^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$",
    re.IGNORECASE,
)


@dataclass
class Contact:
    """Represents a lead contact person.

    Contact is intentionally lightweight to support scraping and enrichment
    flows without requiring deep profile data.
    """

    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    address: Address | None = None
    linkedin_url: str | None = None

    def __post_init__(self) -> None:
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        if self.email is not None:
            self.email = self.email.strip()
        if self.phone is not None:
            self.phone = self.phone.strip()
        if self.title is not None:
            self.title = self.title.strip()
        if self.linkedin_url is not None:
            self.linkedin_url = self.linkedin_url.strip()
        self.validate()

    def validate(self) -> None:
        """Validate contact data consistency."""
        if not self.first_name and not self.last_name:
            raise ValueError("Contact must include at least one of first_name or last_name")
        if self.email and not EMAIL_REGEXP.match(self.email):
            raise ValueError(f"Invalid email address: {self.email}")
        if self.linkedin_url and not URL_REGEXP.match(self.linkedin_url):
            raise ValueError(f"Invalid linkedin_url: {self.linkedin_url}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize contact to JSON-safe dictionary."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "title": self.title,
            "address": self.address.to_dict() if self.address else None,
            "linkedin_url": self.linkedin_url,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Contact:
        """Create a Contact from serialized data."""
        address_data = raw.get("address")
        return cls(
            first_name=raw.get("first_name", ""),
            last_name=raw.get("last_name", ""),
            email=raw.get("email"),
            phone=raw.get("phone"),
            title=raw.get("title"),
            linkedin_url=raw.get("linkedin_url"),
            address=Address.from_dict(address_data) if isinstance(address_data, dict) else None,
        )

    def __repr__(self) -> str:
        return (
            f"Contact(first_name={self.first_name!r}, last_name={self.last_name!r}, "
            f"email={self.email!r}, phone={self.phone!r}, title={self.title!r})"
        )
