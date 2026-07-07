from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from models import Address, Contact, Company, Lead
from scrapers.business_directory.constants import (
    ADDRESS_SELECTOR,
    CATEGORY_SELECTOR,
    LISTING_SELECTOR,
    NAME_SELECTOR,
    PHONE_SELECTOR,
    WEBSITE_SELECTOR,
)


def parse_listing(listing: Any, base_url: str) -> Lead | None:
    """Parse a single business listing into a Lead object."""
    try:
        name = listing.select_one(NAME_SELECTOR).get_text(strip=True)
        phone = listing.select_one(PHONE_SELECTOR).get_text(strip=True) if listing.select_one(PHONE_SELECTOR) else None
        website_tag = listing.select_one(WEBSITE_SELECTOR)
        website = website_tag["href"].strip() if website_tag and website_tag.has_attr("href") else None
        category = listing.select_one(CATEGORY_SELECTOR).get_text(strip=True) if listing.select_one(CATEGORY_SELECTOR) else ""
        address_text = listing.select_one(ADDRESS_SELECTOR).get_text(strip=True) if listing.select_one(ADDRESS_SELECTOR) else ""

        street_address, city, region, postal_code, country = _split_address(address_text)

        address = Address(
            street_address=street_address,
            city=city,
            region=region,
            postal_code=postal_code,
            country=country,
        )

        company = Company(
            name=name,
            website=website,
            industry=category,
            headquarters=address,
        )
        contact = Contact(
            first_name="",
            last_name="",
            phone=phone,
        )

        return Lead(
            company=company,
            contact=contact,
            source=base_url,
            industry=category,
            confidence_score=0.5,
            status="new",
            tags=[category] if category else [],
            notes=[],
        )
    except Exception:
        return None


def _split_address(raw_address: str) -> tuple[str, str, str, str, str]:
    """Attempt to split an address string into structured fields."""
    if not raw_address:
        return "", "", "", "", ""
    parts = [part.strip() for part in raw_address.replace("\n", ",").split(",") if part.strip()]
    if len(parts) >= 4:
        street_address = parts[0]
        city = parts[-3]
        region = parts[-2]
        postal_code = parts[-1].split(" ")[0]
        country = "United States"
    elif len(parts) == 3:
        street_address, city, region = parts
        postal_code = ""
        country = "United States"
    else:
        street_address = raw_address
        city = ""
        region = ""
        postal_code = ""
        country = ""
    return street_address, city, region, postal_code, country
