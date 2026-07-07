from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LeadStatus(str, Enum):
    """Lead lifecycle state."""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"
    REJECTED = "rejected"


class Industry(str, Enum):
    """Common lead industry classifications."""

    SOFTWARE = "software"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    OTHER = "other"


def parse_enum(enum_class: type[Enum], value: str | Enum) -> Enum:
    """Convert a string or Enum to a concrete Enum member."""
    if isinstance(value, enum_class):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        try:
            return enum_class(normalized)
        except ValueError:
            try:
                return enum_class[normalized.upper()]
            except KeyError as exc:
                raise ValueError(f"Unknown {enum_class.__name__} value: {value}") from exc
    raise TypeError(f"Value must be a str or {enum_class.__name__}, got {type(value).__name__}")
