from __future__ import annotations

import json
import logging
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

    return app


if __name__ == "__main__":
    config = init_config()
    db_manager = DatabaseManager(config.database)
    db_manager.create_tables()

    app = create_api_app(db_manager)
    app.run(debug=True, port=5000, host="0.0.0.0")
