from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.models import LeadORM
from models import Company, Contact, Lead


class DuplicateDetectionRule(str):
    WEBSITE = "website"
    PHONE = "phone"
    BUSINESS_NAME_CITY = "business_name_city"


class LeadRepository:
    """Repository for lead persistence and retrieval."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._logger = logging.getLogger(self.__class__.__name__)

    def create_lead(self, lead: Lead, duplicate_rules: list[str] | None = None) -> Lead:
        """Persist a new lead if no duplicate record exists."""
        duplicate_rules = duplicate_rules or [
            DuplicateDetectionRule.WEBSITE,
            DuplicateDetectionRule.PHONE,
            DuplicateDetectionRule.BUSINESS_NAME_CITY,
        ]
        if self._find_duplicate(lead, duplicate_rules) is not None:
            raise ValueError("Duplicate lead detected")

        orm_lead = self._to_orm(lead)
        self._session.add(orm_lead)
        try:
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            self._logger.error("Database integrity error while creating lead", exc_info=exc)
            raise
        self._logger.info("Created new lead", extra={"lead_id": orm_lead.id})
        return self._from_orm(orm_lead)

    def get_lead(self, lead_id: str) -> Lead | None:
        """Retrieve a lead by primary key."""
        statement = select(LeadORM).where(LeadORM.id == lead_id)
        result = self._session.execute(statement).scalar_one_or_none()
        return self._from_orm(result) if result else None

    def update_lead(self, lead_id: str, fields: dict[str, Any]) -> Lead | None:
        """Update an existing lead by ID."""
        statement = select(LeadORM).where(LeadORM.id == lead_id)
        orm_lead = self._session.execute(statement).scalar_one_or_none()
        if orm_lead is None:
            return None

        for key, value in fields.items():
            if hasattr(orm_lead, key):
                setattr(orm_lead, key, value)
        orm_lead.updated_at = datetime.now(timezone.utc)
        self._session.flush()
        self._logger.info("Updated lead", extra={"lead_id": lead_id})
        return self._from_orm(orm_lead)

    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead by ID."""
        statement = select(LeadORM).where(LeadORM.id == lead_id)
        orm_lead = self._session.execute(statement).scalar_one_or_none()
        if orm_lead is None:
            return False
        self._session.delete(orm_lead)
        self._session.flush()
        self._logger.info("Deleted lead", extra={"lead_id": lead_id})
        return True

    def list_leads(self, limit: int = 100, offset: int = 0) -> list[Lead]:
        """Return a paginated list of leads."""
        statement = select(LeadORM).limit(limit).offset(offset)
        results = self._session.execute(statement).scalars().all()
        return [self._from_orm(row) for row in results]

    def search_leads(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        """Search leads by company, contact, source, or address."""
        query_value = f"%{query}%"
        statement = select(LeadORM).where(
            or_(
                LeadORM.company_name.ilike(query_value),
                LeadORM.contact_first_name.ilike(query_value),
                LeadORM.contact_last_name.ilike(query_value),
                LeadORM.contact_email.ilike(query_value),
                LeadORM.source.ilike(query_value),
                LeadORM.address_city.ilike(query_value),
            )
        ).limit(limit).offset(offset)
        results = self._session.execute(statement).scalars().all()
        return [self._from_orm(row) for row in results]

    def _find_duplicate(self, lead: Lead, rules: list[str]) -> LeadORM | None:
        filters = []
        if DuplicateDetectionRule.WEBSITE in rules and lead.company.website:
            filters.append(LeadORM.company_website == lead.company.website)
        if DuplicateDetectionRule.PHONE in rules and lead.contact.phone:
            filters.append(LeadORM.contact_phone == lead.contact.phone)
        if DuplicateDetectionRule.BUSINESS_NAME_CITY in rules and lead.contact.address:
            filters.append(
                and_(
                    LeadORM.company_name == lead.company.name,
                    LeadORM.address_city == lead.contact.address.city,
                )
            )
        if not filters:
            return None
        statement = select(LeadORM).where(or_(*filters))
        return self._session.execute(statement).scalar_one_or_none()

    def _to_orm(self, lead: Lead) -> LeadORM:
        return LeadORM(
            id=str(lead.id),
            company_name=lead.company.name,
            company_website=lead.company.website,
            company_domain=lead.company.domain,
            company_industry=(lead.company.industry.value if isinstance(lead.company.industry, Enum) else lead.company.industry),
            contact_first_name=lead.contact.first_name,
            contact_last_name=lead.contact.last_name,
            contact_email=lead.contact.email,
            contact_phone=lead.contact.phone,
            source=lead.source,
            confidence_score=lead.confidence_score,
            status=(lead.status.value if isinstance(lead.status, Enum) else lead.status),
            tags=lead.tags,
            notes=lead.notes,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
            address_city=lead.contact.address.city if lead.contact.address else None,
            address_region=lead.contact.address.region if lead.contact.address else None,
            address_postal_code=lead.contact.address.postal_code if lead.contact.address else None,
            address_country=lead.contact.address.country if lead.contact.address else None,
        )

    def _from_orm(self, orm_lead: LeadORM) -> Lead:
        company = {
            "name": orm_lead.company_name,
            "website": orm_lead.company_website,
            "domain": orm_lead.company_domain,
            "industry": orm_lead.company_industry,
        }
        contact = {
            "first_name": orm_lead.contact_first_name,
            "last_name": orm_lead.contact_last_name,
            "email": orm_lead.contact_email,
            "phone": orm_lead.contact_phone,
        }
        address = None
        if orm_lead.address_city or orm_lead.address_region or orm_lead.address_postal_code or orm_lead.address_country:
            address = {
                "street_address": "",
                "city": orm_lead.address_city or "",
                "region": orm_lead.address_region or "",
                "postal_code": orm_lead.address_postal_code or "",
                "country": orm_lead.address_country or "",
            }
        return Lead(
            id=orm_lead.id,
            company=Company.from_dict(company),
            contact=Contact.from_dict({**contact, "address": address}),
            source=orm_lead.source,
            industry=orm_lead.company_industry or "",
            confidence_score=orm_lead.confidence_score,
            status=orm_lead.status,
            tags=orm_lead.tags or [],
            notes=orm_lead.notes or [],
            created_at=orm_lead.created_at,
            updated_at=orm_lead.updated_at,
        )
