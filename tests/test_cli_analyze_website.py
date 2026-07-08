from __future__ import annotations

import importlib


def test_cli_analyze_website_command(monkeypatch) -> None:
    import main

    class FakeAdapter:
        def __init__(self) -> None:
            self.calls = []

        def fetch(self, url: str):
            self.calls.append(url)
            return []

    monkeypatch.setattr(main, "WebsiteAdapter", FakeAdapter)
    monkeypatch.setattr(main, "DatabaseManager", lambda *args, **kwargs: type("DB", (), {"create_tables": lambda self: None})())
    monkeypatch.setattr(main, "DatabaseSessionManager", lambda *args, **kwargs: type("SessionManager", (), {"session_scope": lambda self: None})())

    exit_code = main.main(["analyze-website", "https://example.com"])
    assert exit_code == 0
