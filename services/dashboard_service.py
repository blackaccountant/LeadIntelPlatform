from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any

from models import Lead


@dataclass(slots=True)
class DashboardSummary:
    total_leads: int
    qualified_leads: int
    pending_leads: int
    exported_leads: int


def render_dashboard_html(leads: list[Lead], summary: DashboardSummary) -> str:
    """Render a simple standalone HTML dashboard for leads and campaign status."""
    lead_rows = []
    for lead in leads:
        company = lead.company
        contact = lead.contact
        lead_rows.append(
            f"""
            <tr>
              <td>{escape(company.name if company else '')}</td>
              <td>{escape(company.website or '') if company else ''}</td>
              <td>{escape(contact.email or '') if contact else ''}</td>
              <td>{escape(str(lead.status.value if hasattr(lead.status, 'value') else lead.status))}</td>
              <td>{escape(str(lead.confidence_score))}</td>
            </tr>
            """
        )
    if not lead_rows:
        lead_rows.append("<tr><td colspan='5'>No leads available yet.</td></tr>")

    return f"""
    <!doctype html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Lead Intelligence Dashboard</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
          .card {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
          .stats {{ display: flex; gap: 12px; flex-wrap: wrap; }}
          .stat {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; min-width: 140px; }}
          table {{ width: 100%; border-collapse: collapse; }}
          th, td {{ border-bottom: 1px solid #e5e7eb; padding: 10px 8px; text-align: left; }}
          th {{ background: #f3f4f6; }}
        </style>
      </head>
      <body>
        <h1>Lead Intelligence Dashboard</h1>
        <div class=\"card\">
          <h2>Campaign Snapshot</h2>
          <div class=\"stats\">
            <div class=\"stat\"><strong>{summary.total_leads}</strong><br/>Total leads</div>
            <div class=\"stat\"><strong>{summary.qualified_leads}</strong><br/>Qualified leads</div>
            <div class=\"stat\"><strong>{summary.pending_leads}</strong><br/>Pending leads</div>
            <div class=\"stat\"><strong>{summary.exported_leads}</strong><br/>Exported leads</div>
          </div>
        </div>
        <div class=\"card\">
          <h2>Leads</h2>
          <table>
            <thead>
              <tr>
                <th>Company</th>
                <th>Website</th>
                <th>Email</th>
                <th>Status</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {''.join(lead_rows)}
            </tbody>
          </table>
        </div>
      </body>
    </html>
    """
