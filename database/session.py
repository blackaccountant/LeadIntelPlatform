from __future__ import annotations

import contextlib
from sqlalchemy.orm import Session

from database.database import DatabaseManager


class DatabaseSessionManager:
    """Context manager for SQLAlchemy sessions."""

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._database_manager = database_manager

    def __enter__(self) -> Session:
        self._session = self._database_manager.session_factory()
        return self._session

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()

    @contextlib.contextmanager
    def session_scope(self) -> Session:
        """Yield a transactional session in a context manager."""
        session = self._database_manager.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
