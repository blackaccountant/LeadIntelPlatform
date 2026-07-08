from __future__ import annotations

from typing import Any

from models import Address, Contact, Company, Lead


def parse_listing(listing: Any, base_url: str) -> Lead | None:
    """Parse a single business listing into a Lead object."""
    try:
        name = listing.select_one(".listing-name").get_text(strip=True)
        phone = listing.select_one(".listing-phone").get_text(strip=True) if listing.select_one(".listing-phone") else None
        website_tag = listing.select_one(".listing-website a")
        website = website_tag["href"].strip() if website_tag and website_tag.has_attr("href") else None
        category = listing.select_one(".listing-category").get_text(strip=True) if listing.select_one(".listing-category") else ""
        address_text = listing.select_one(".listing-address").get_text(strip=True) if listing.select_one(".listing-address") else ""

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
        contact = Contact(first_name="", last_name="", phone=phone)

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
