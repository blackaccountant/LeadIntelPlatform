from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import init_config
from database.database import DatabaseManager
from database.session import DatabaseSessionManager
from database.repository import LeadRepository


def create_api_app(db_manager: DatabaseManager) -> Flask:
    """Create a Flask API application for the Lead Intelligence Platform."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for GitHub Pages
    session_manager = DatabaseSessionManager(db_manager)
    logger = logging.getLogger(__name__)

    # In-memory campaign job store: job_id -> {status, progress, summary, error}
    _jobs: dict[str, dict[str, Any]] = {}

    @app.route("/api/leads", methods=["GET"])
    def get_leads() -> tuple[Any, int]:
        """Retrieve all leads as JSON."""
        try:
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                leads = repository.list_all_leads()

            leads_data = [
                {
                    "id": str(lead.id),
                    "company": {
                        "name": lead.company.name if lead.company else "",
                        "website": lead.company.website if lead.company else None,
                        "industry": lead.company.industry.value if hasattr(lead.company.industry, "value") and lead.company else "",
                    },
                    "website": lead.company.website if lead.company else None,
                    "contact_name": (
                        f"{lead.contact.first_name} {lead.contact.last_name}".strip()
                        if lead.contact
                        else None
                    ),
                    "contact_title": lead.contact.title if lead.contact else None,
                    "contact_email": lead.contact.email if lead.contact else None,
                    "contact_phone": lead.contact.phone if lead.contact else None,
                    "email": lead.contact.email if lead.contact else None,
                    "phone": lead.contact.phone if lead.contact else None,
                    "status": lead.status.value if hasattr(lead.status, "value") else str(lead.status),
                    "confidence_score": lead.confidence_score,
                    "source": lead.source,
                    "tags": lead.tags,
                    "notes": lead.notes,
                }
                for lead in leads
            ]
            return jsonify(leads_data), 200
        except Exception as exc:
            logger.exception("Failed to fetch leads", exc_info=exc)
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/leads/<lead_id>", methods=["GET"])
    def get_lead(lead_id: str) -> tuple[Any, int]:
        """Retrieve a single lead by ID."""
        try:
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                lead = repository.get_lead(lead_id)

            if lead is None:
                return jsonify({"error": "Lead not found"}), 404

            lead_data = {
                "id": str(lead.id),
                "company": {
                    "name": lead.company.name if lead.company else "",
                    "website": lead.company.website if lead.company else None,
                    "industry": lead.company.industry.value if hasattr(lead.company.industry, "value") and lead.company else "",
                },
                "website": lead.company.website if lead.company else None,
                "contact_name": (
                    f"{lead.contact.first_name} {lead.contact.last_name}".strip()
                    if lead.contact
                    else None
                ),
                "contact_title": lead.contact.title if lead.contact else None,
                "contact_email": lead.contact.email if lead.contact else None,
                "contact_phone": lead.contact.phone if lead.contact else None,
                "email": lead.contact.email if lead.contact else None,
                "phone": lead.contact.phone if lead.contact else None,
                "status": lead.status.value if hasattr(lead.status, "value") else str(lead.status),
                "confidence_score": lead.confidence_score,
                "source": lead.source,
                "tags": lead.tags,
                "notes": lead.notes,
            }
            return jsonify(lead_data), 200
        except Exception as exc:
            logger.exception("Failed to fetch lead", exc_info=exc)
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/stats", methods=["GET"])
    def get_stats() -> tuple[Any, int]:
        """Retrieve campaign statistics."""
        try:
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                total = repository.count_leads()
                leads = repository.list_all_leads()

            qualified = sum(1 for lead in leads if getattr(lead.status, "value", lead.status) == "qualified")
            pending = sum(1 for lead in leads if getattr(lead.status, "value", lead.status) in {"new", "contacted"})

            stats = {
                "total_leads": total,
                "qualified_leads": qualified,
                "pending_leads": pending,
                "qualification_rate": (qualified / total * 100) if total > 0 else 0,
            }
            return jsonify(stats), 200
        except Exception as exc:
            logger.exception("Failed to fetch stats", exc_info=exc)
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/health", methods=["GET"])
    def health_check() -> tuple[Any, int]:
        """Health check endpoint."""
        return jsonify({"status": "ok"}), 200

    @app.route("/api/campaign/start", methods=["POST"])
    def start_campaign() -> tuple[Any, int]:
        """Start a lead discovery campaign in a background thread."""
        try:
            body = request.get_json(silent=True) or {}
            source = str(body.get("source", "opencorporates"))
            keyword = str(body.get("keyword", "software"))
            industry = str(body.get("industry", "")) or None
            location = str(body.get("location", "US")) or "US"
            limit = min(int(body.get("limit", 20)), 100)
            website_url = str(body.get("website_url", "")).strip() or None

            job_id = str(uuid.uuid4())
            _jobs[job_id] = {
                "status": "running",
                "progress": 0,
                "message": "Starting campaign…",
                "summary": None,
                "error": None,
            }

            def run_campaign() -> None:
                try:
                    from adapters.opencorporates.adapter import OpenCorporatesAdapter
                    from adapters.website.adapter import WebsiteAdapter
                    from adapters.business_directory.adapter import BusinessDirectoryAdapter
                    from adapters.directory_crawler.adapter import DirectoryCrawlerAdapter
                    from services.campaign_service import CampaignCriteria, CampaignManager

                    _jobs[job_id]["message"] = "Initializing adapters…"
                    _jobs[job_id]["progress"] = 10

                    adapters = []
                    if source == "directory":
                        # Crawl a business directory listing page
                        adapters.append(DirectoryCrawlerAdapter())
                    elif website_url:
                        adapters.append(WebsiteAdapter())
                    elif source == "opencorporates":
                        adapters.append(OpenCorporatesAdapter())
                    else:
                        adapters.append(BusinessDirectoryAdapter(
                            category=industry or keyword,
                            location=location,
                        ))

                    criteria = CampaignCriteria(
                        country=location,
                        industry=industry,
                        keyword=keyword if not website_url else None,
                        limit=limit,
                    )

                    _jobs[job_id]["message"] = "Fetching leads from source…"
                    _jobs[job_id]["progress"] = 30

                    # If website_url, override the fetch call
                    if source == "directory" and website_url:
                        dir_adapter = adapters[0]
                        _jobs[job_id]["message"] = "Crawling directory listing pages…"
                        _jobs[job_id]["progress"] = 30
                        raw_leads = dir_adapter.fetch(
                            url=website_url,
                            keyword=keyword,
                            location=location,
                            page_limit=3,
                        )
                        _jobs[job_id]["progress"] = 70
                        _jobs[job_id]["message"] = f"Saving {len(raw_leads)} discovered leads…"
                        saved = 0
                        with session_manager.session_scope() as session:
                            repo = LeadRepository(session)
                            for lead in raw_leads:
                                try:
                                    repo.create_lead(lead)
                                    session.commit()
                                    saved += 1
                                except Exception:
                                    pass
                        summary = {"discovered": len(raw_leads), "saved": saved, "source": f"directory:{website_url}"}
                    elif website_url:
                        web_adapter = adapters[0]
                        raw_leads = web_adapter.fetch(url=website_url)
                        _jobs[job_id]["progress"] = 70
                        _jobs[job_id]["message"] = f"Saving {len(raw_leads)} discovered leads…"
                        saved = 0
                        with session_manager.session_scope() as session:
                            repo = LeadRepository(session)
                            for lead in raw_leads:
                                try:
                                    repo.create_lead(lead)
                                    session.commit()
                                    saved += 1
                                except Exception:
                                    pass
                        summary = {"discovered": len(raw_leads), "saved": saved, "source": f"website:{website_url}"}
                    else:
                        with session_manager.session_scope() as session:
                            repo = LeadRepository(session)
                            manager = CampaignManager(repository=repo, logger=logger)
                            _jobs[job_id]["progress"] = 50
                            result = manager.run(adapters, criteria)
                            _jobs[job_id]["progress"] = 80
                        summary = {
                            "discovered": result.discovered,
                            "qualified": result.qualified,
                            "rejected": result.rejected,
                            "saved": result.saved,
                            "source": source,
                        }

                    _jobs[job_id]["status"] = "done"
                    _jobs[job_id]["progress"] = 100
                    _jobs[job_id]["message"] = f"Done! Saved {summary.get('saved', 0)} new leads."
                    _jobs[job_id]["summary"] = summary
                except Exception as exc:
                    logger.exception("Campaign job failed", exc_info=exc)
                    _jobs[job_id]["status"] = "error"
                    _jobs[job_id]["error"] = str(exc)
                    _jobs[job_id]["message"] = f"Error: {exc}"

            thread = threading.Thread(target=run_campaign, daemon=True)
            thread.start()

            return jsonify({"job_id": job_id, "status": "running"}), 202
        except Exception as exc:
            logger.exception("Failed to start campaign", exc_info=exc)
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/campaign/status/<job_id>", methods=["GET"])
    def campaign_status(job_id: str) -> tuple[Any, int]:
        """Poll campaign job status."""
        job = _jobs.get(job_id)
        if job is None:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(job), 200

    @app.route("/api/leads/<lead_id>", methods=["DELETE"])
    def delete_lead(lead_id: str) -> tuple[Any, int]:
        """Delete a lead by ID."""
        try:
            with session_manager.session_scope() as session:
                repository = LeadRepository(session)
                lead = repository.get_lead(lead_id)
                if lead is None:
                    return jsonify({"error": "Lead not found"}), 404
                repository.delete_lead(lead_id)
                session.commit()
            return jsonify({"deleted": lead_id}), 200
        except Exception as exc:
            logger.exception("Failed to delete lead", exc_info=exc)
            return jsonify({"error": str(exc)}), 500

    return app


if __name__ == "__main__":
    config = init_config()
    db_manager = DatabaseManager(config.database)
    db_manager.create_tables()

    app = create_api_app(db_manager)
    app.run(debug=True, port=5000, host="0.0.0.0")
