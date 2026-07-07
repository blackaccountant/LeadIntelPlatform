from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Address:
    """Represents a normalized mailing address.

    This dataclass is intentionally simple so it can be nested in other
    core domain models and serialized easily.
    """

    street_address: str
    city: str
    region: str
    postal_code: str
    country: str = "United States"
    line2: str | None = None

    def __post_init__(self) -> None:
        self.street_address = self.street_address.strip()
        self.city = self.city.strip()
        self.region = self.region.strip()
        self.postal_code = self.postal_code.strip()
        self.country = self.country.strip()
        if self.line2 is not None:
            self.line2 = self.line2.strip()
        self.validate()

    def validate(self) -> None:
        """Validate required address fields."""
        if not self.street_address:
            raise ValueError("street_address must not be empty")
        if not self.city:
            raise ValueError("city must not be empty")
        if not self.region:
            raise ValueError("region must not be empty")
        if not self.postal_code:
            raise ValueError("postal_code must not be empty")
        if not self.country:
            raise ValueError("country must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Serialize address to a JSON-safe dictionary."""
        return {
            "street_address": self.street_address,
            "line2": self.line2,
            "city": self.city,
            "region": self.region,
            "postal_code": self.postal_code,
            "country": self.country,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Address:
        """Create an Address from serialized data."""
        return cls(
            street_address=raw.get("street_address", ""),
            line2=raw.get("line2"),
            city=raw.get("city", ""),
            region=raw.get("region", ""),
            postal_code=raw.get("postal_code", ""),
            country=raw.get("country", "United States"),
        )

    def __repr__(self) -> str:
        return (
            f"Address(street_address={self.street_address!r}, city={self.city!r}, "
            f"region={self.region!r}, postal_code={self.postal_code!r}, country={self.country!r})"
        )
