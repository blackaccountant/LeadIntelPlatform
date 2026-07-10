"""Services package for orchestration, qualification, and campaign workflows."""

from .campaign_service import CampaignCriteria, CampaignManager, CampaignSummary
from .lead_ingestion_service import LeadIngestionService
from .qualification_service import LeadQualificationService, QualificationResult

__all__ = [
    "CampaignCriteria",
    "CampaignManager",
    "CampaignSummary",
    "LeadIngestionService",
    "LeadQualificationService",
    "QualificationResult",
]

__version__ = "0.1.0"
