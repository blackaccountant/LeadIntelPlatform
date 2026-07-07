"""
Models Package
==============

Defines data models and dataclasses for application entities.

Modules:
    - enums: shared enum definitions
    - address: Address dataclass
    - contact: Contact dataclass
    - company: Company dataclass
    - lead: Lead dataclass
"""

from .address import Address
from .company import Company
from .contact import Contact
from .enums import Industry, LeadStatus
from .lead import Lead

__all__ = [
    "Address",
    "Company",
    "Contact",
    "Industry",
    "Lead",
    "LeadStatus",
]

__version__ = "0.1.0"
