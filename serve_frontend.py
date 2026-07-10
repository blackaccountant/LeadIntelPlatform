#!/usr/bin/env python3
"""
Simple HTTP server for the frontend dashboard.

This script serves the frontend files from the frontend/ directory
on localhost:8000, allowing local testing and development.
"""

import os
import http.server
import socketserver
from pathlib import Path


class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the frontend."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def log_message(self, format, *args):
        """Log requests."""
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    PORT = 8000
    
    # Change to frontend directory
    os.chdir(Path(__file__).parent / "frontend")
    
    Handler = FrontendHandler

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Frontend server running at http://localhost:{PORT}")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error: {e}")
