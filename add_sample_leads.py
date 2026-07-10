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
        
        # Sample leads
        sample_data = [
            {
                "company_name": "TechFlow Solutions",
                "website": "https://techflow.example",
                "industry": "software",
                "email": "sales@techflow.example",
                "phone": "+1 (555) 111-1111",
                "status": "qualified",
                "confidence": 0.95,
                "source": "website_crawler",
            },
            {
                "company_name": "DataViz Analytics",
                "website": "https://dataviz.example",
                "industry": "software",
                "email": "contact@dataviz.example",
                "phone": "+1 (555) 222-2222",
                "status": "new",
                "confidence": 0.88,
                "source": "website_crawler",
            },
            {
                "company_name": "CloudSync Corp",
                "website": "https://cloudsync.example",
                "industry": "cloud",
                "email": "info@cloudsync.example",
                "phone": "+1 (555) 333-3333",
                "status": "qualified",
                "confidence": 0.92,
                "source": "opencorporates",
            },
            {
                "company_name": "Secure Networks Inc",
                "website": "https://securenetworks.example",
                "industry": "security",
                "email": "business@securenetworks.example",
                "phone": "+1 (555) 444-4444",
                "status": "new",
                "confidence": 0.85,
                "source": "website_crawler",
            },
            {
                "company_name": "Mobile Innovations",
                "website": "https://mobileinnovations.example",
                "industry": "mobile",
                "email": "partnerships@mobileinnovations.example",
                "phone": "+1 (555) 555-5555",
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
            
            contact = Contact(
                first_name="Sales",
                last_name="Team",
                email=data["email"],
                phone=data["phone"],
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
