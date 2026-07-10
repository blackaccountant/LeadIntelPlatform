"""Test script to add sample leads to the database."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import init_config
from database.database import DatabaseManager
from database.repository import LeadRepository
from database.session import DatabaseSessionManager
from models import Address, Company, Contact, Lead


def add_sample_leads():
    """Add sample leads to the database for testing."""
    config = init_config()
    db_manager = DatabaseManager(config.database)
    db_manager.create_tables()
    
    session_manager = DatabaseSessionManager(db_manager)
    
    with session_manager.session_scope() as session:
        repository = LeadRepository(session)
        
        # Sample leads with CEO/Founder details
        sample_data = [
            {
                "company_name": "TechFlow Solutions",
                "website": "https://techflow.example",
                "industry": "software",
                "contact_name": "Michael Chen",
                "contact_title": "CEO & Founder",
                "contact_email": "michael.chen@techflow.example",
                "contact_phone": "+1 (555) 111-2001",
                "status": "qualified",
                "confidence": 0.95,
                "source": "website_crawler",
            },
            {
                "company_name": "DataViz Analytics",
                "website": "https://dataviz.example",
                "industry": "software",
                "contact_name": "Sarah Rodriguez",
                "contact_title": "Founder & CTO",
                "contact_email": "sarah@dataviz.example",
                "contact_phone": "+1 (555) 222-2001",
                "status": "new",
                "confidence": 0.88,
                "source": "website_crawler",
            },
            {
                "company_name": "CloudSync Corp",
                "website": "https://cloudsync.example",
                "industry": "cloud",
                "contact_name": "James Patterson",
                "contact_title": "President & CEO",
                "contact_email": "james.patterson@cloudsync.example",
                "contact_phone": "+1 (555) 333-2001",
                "status": "qualified",
                "confidence": 0.92,
                "source": "opencorporates",
            },
            {
                "company_name": "Secure Networks Inc",
                "website": "https://securenetworks.example",
                "industry": "security",
                "contact_name": "Dr. Priya Sharma",
                "contact_title": "Founder & Chief Security Officer",
                "contact_email": "priya.sharma@securenetworks.example",
                "contact_phone": "+1 (555) 444-2001",
                "status": "new",
                "confidence": 0.85,
                "source": "website_crawler",
            },
            {
                "company_name": "Mobile Innovations",
                "website": "https://mobileinnovations.example",
                "industry": "mobile",
                "contact_name": "David Thompson",
                "contact_title": "Owner & Executive Director",
                "contact_email": "david.thompson@mobileinnovations.example",
                "contact_phone": "+1 (555) 555-2001",
                "status": "contacted",
                "confidence": 0.90,
                "source": "business_registry",
            },
        ]
        
        for data in sample_data:
            company = Company(
                name=data["company_name"],
                website=data["website"],
                domain=data["website"].replace("https://", "").replace("http://", ""),
                industry=data["industry"],
            )
            
            # Parse contact name
            names = data["contact_name"].split(" ", 1)
            first_name = names[0]
            last_name = names[1] if len(names) > 1 else ""
            
            contact = Contact(
                first_name=first_name,
                last_name=last_name,
                email=data["contact_email"],
                phone=data["contact_phone"],
                title=data["contact_title"],
            )
            
            lead = Lead(
                company=company,
                contact=contact,
                status=data["status"],
                confidence_score=data["confidence"],
                source=data["source"],
                tags=["sample", data["industry"]],
            )
            
            repository.create_lead(lead)
            session.commit()
            print(f"✓ Added: {data['company_name']}")
    
    print("\nSample leads added successfully!")


if __name__ == "__main__":
    add_sample_leads()
