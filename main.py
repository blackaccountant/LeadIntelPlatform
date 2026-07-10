"""
Main Entry Point
================

Lead Intelligence Platform - AI-assisted lead generation system.

This module serves as the application entry point, initializing the
configuration, logging, and orchestrating command-line flows.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Optional

from config import init_config
from database.database import DatabaseManager
from database.repository import LeadRepository
from database.session import DatabaseSessionManager
from logging_config import get_logger, setup_logging
from adapters.business_directory import BusinessDirectoryAdapter
from adapters.opencorporates import OpenCorporatesAdapter
from adapters.website import WebsiteAdapter
from models import Lead
from services.campaign_service import CampaignCriteria, CampaignManager
from services.dashboard_service import DashboardSummary, render_dashboard_html
from services.lead_ingestion_service import LeadIngestionService


logger = get_logger(__name__)


def build_adapter(source: str, category: str, location: str, pages: int) -> object:
    """Return a configured adapter instance for the selected source."""
    supported = {
        "business_directory": BusinessDirectoryAdapter,
        "opencorporates": OpenCorporatesAdapter,
    }
    if source not in supported:
        raise ValueError(f"Unsupported source '{source}'. Supported sources: {', '.join(supported)}")
    if source == "business_directory":
        return supported[source](category=category, location=location)
    return supported[source]()


def export_to_csv(leads: list[Lead], destination: Path) -> None:
    """Export lead rows to CSV."""
    export_path = destination
    export_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "company_name",
        "company_website",
        "company_domain",
        "company_industry",
        "contact_phone",
        "contact_email",
        "source",
        "confidence_score",
        "status",
        "tags",
        "notes",
        "created_at",
        "updated_at",
        "address_city",
        "address_region",
        "address_postal_code",
        "address_country",
    ]

    with export_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow({
                "id": str(lead.id),
                "company_name": lead.company.name,
                "company_website": lead.company.website or "",
                "company_domain": lead.company.domain or "",
                "company_industry": lead.company.industry.value if hasattr(lead.company.industry, "value") else str(lead.company.industry),
                "contact_phone": lead.contact.phone or "",
                "contact_email": lead.contact.email or "",
                "source": lead.source,
                "confidence_score": str(lead.confidence_score),
                "status": lead.status.value if hasattr(lead.status, "value") else str(lead.status),
                "tags": ",".join(lead.tags),
                "notes": " | ".join(lead.notes),
                "created_at": lead.created_at.isoformat(),
                "updated_at": lead.updated_at.isoformat(),
                "address_city": lead.contact.address.city if lead.contact.address else "",
                "address_region": lead.contact.address.region if lead.contact.address else "",
                "address_postal_code": lead.contact.address.postal_code if lead.contact.address else "",
                "address_country": lead.contact.address.country if lead.contact.address else "",
            })
    logger.info("Exported leads to CSV", extra={"path": str(export_path), "count": len(leads)})


def configure_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lead Intelligence Platform CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scrape_parser = subparsers.add_parser("scrape", help="Run an adapter and ingest leads")
    scrape_parser.add_argument("--source", default="business_directory", help="Adapter source name")
    scrape_parser.add_argument("--category", default="software", help="Business category to search")
    scrape_parser.add_argument("--location", default="United States", help="Location for the search")
    scrape_parser.add_argument("--pages", type=int, default=5, help="Maximum number of pages to fetch")
    scrape_parser.add_argument("--export-path", default="exports/scraped_leads.csv", help="Path to export saved leads")

    export_parser = subparsers.add_parser("export", help="Export all stored leads to CSV")
    export_parser.add_argument("--output", default="exports/all_leads.csv", help="CSV destination path")

    campaign_parser = subparsers.add_parser("campaign", help="Run an adapter-driven lead discovery campaign")
    campaign_parser.add_argument("--country", default="US", help="Country code or country name")
    campaign_parser.add_argument("--state", default=None, help="State or region")
    campaign_parser.add_argument("--city", default=None, help="City")
    campaign_parser.add_argument("--industry", default=None, help="Industry keyword")
    campaign_parser.add_argument("--keyword", default=None, help="Search keyword")
    campaign_parser.add_argument("--limit", type=int, default=100, help="Maximum number of leads to process")
    campaign_parser.add_argument("--export", default=None, help="Optional CSV export path")
    campaign_parser.add_argument("--ai", action="store_true", help="Enable enrichment mode (stubbed for compatibility)")
    campaign_parser.add_argument("--dry-run", action="store_true", help="Validate campaign inputs without persisting")

    analyze_parser = subparsers.add_parser("analyze-website", help="Analyze a company website")
    analyze_parser.add_argument("url", help="Company website URL")

    dashboard_parser = subparsers.add_parser("dashboard", help="Render a local HTML dashboard")
    dashboard_parser.add_argument("--output", default="exports/dashboard.html", help="Path to write the dashboard HTML")

    api_parser = subparsers.add_parser("api", help="Start the REST API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="API server host")
    api_parser.add_argument("--port", type=int, default=5000, help="API server port")
    api_parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    stats_parser = subparsers.add_parser("stats", help="Show lead repository statistics")

    return parser


def main(args: Optional[list[str]] = None) -> int:
    try:
        config = init_config()
        setup_logging(config.logging)

        parser = configure_arg_parser()
        parsed = parser.parse_args(args)

        logger.info("Starting Lead Intelligence Platform CLI", extra={"command": parsed.command})

        db_manager = DatabaseManager(config.database)
        db_manager.create_tables()
        session_manager = DatabaseSessionManager(db_manager)

        if parsed.command == "scrape":
            adapter = build_adapter(parsed.source, parsed.category, parsed.location, parsed.pages)
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                ingestion = LeadIngestionService(
                    repository=repository,
                    export_path=parsed.export_path,
                )
                metrics = ingestion.ingest(adapter, page_limit=parsed.pages)
            logger.info("Scrape summary", extra=metrics)
            print(f"Scrape completed: {metrics}")

        elif parsed.command == "export":
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                leads = repository.list_all_leads()
            export_to_csv(leads, Path(parsed.output))
            print(f"Exported {len(leads)} leads to {parsed.output}")

        elif parsed.command == "analyze-website":
            adapter = WebsiteAdapter()
            leads = adapter.fetch(parsed.url)
            if leads:
                lead = leads[0]
                print(f"Analyzed {lead.company.website}: {lead.company.name}")
                print(f"Email: {lead.contact.email or ''}")
                print(f"Phone: {lead.contact.phone or ''}")
            else:
                print("No website intelligence found")

        elif parsed.command == "campaign":
            criteria = CampaignCriteria(
                country=parsed.country,
                state=parsed.state,
                city=parsed.city,
                industry=parsed.industry,
                keyword=parsed.keyword,
                limit=parsed.limit,
                ai=parsed.ai,
                dry_run=parsed.dry_run,
                export=parsed.export,
            )
            adapters = [
                BusinessDirectoryAdapter(category=criteria.industry or "software", location=criteria.state or criteria.country or "United States"),
                OpenCorporatesAdapter(),
            ]
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                manager = CampaignManager(repository)
                summary = manager.run(adapters, criteria)
            print(f"Campaign complete: discovered={summary.discovered}, qualified={summary.qualified}, rejected={summary.rejected}, saved={summary.saved}")
            if summary.output_path:
                print(f"Exported campaign results to {summary.output_path}")

        elif parsed.command == "dashboard":
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                leads = repository.list_all_leads()
            summary = DashboardSummary(
                total_leads=len(leads),
                qualified_leads=sum(1 for lead in leads if getattr(lead, "status", None) == "qualified"),
                pending_leads=sum(1 for lead in leads if getattr(lead, "status", None) in {"new", "contacted"}),
                exported_leads=0,
            )
            html = render_dashboard_html(leads, summary)
            output_path = Path(parsed.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            print(f"Dashboard written to {output_path}")

        elif parsed.command == "api":
            try:
                from api import create_api_app
            except ImportError:
                logger.error("Flask is not installed. Install with: pip install flask flask-cors")
                print("Error: Flask is not installed. Install with: pip install flask flask-cors")
                return 1
            app = create_api_app(db_manager)
            print(f"Starting API server on {parsed.host}:{parsed.port}")
            app.run(host=parsed.host, port=parsed.port, debug=parsed.debug)

        elif parsed.command == "stats":
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                total = repository.count_leads()
            print(f"Total leads in database: {total}")

        return 0

    except Exception as exc:
        logger.exception("Command failed", exc_info=exc)
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
