from __future__ import annotations

import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import DatabaseConfig
from database.models import Base


class DatabaseManager:
    """Manage database engine and schema lifecycle."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._engine = self._create_engine()
        self._session_factory = sessionmaker(
            bind=self._engine,
            future=True,
            expire_on_commit=False,
        )

    def _create_engine(self) -> Engine:
        engine = create_engine(
            self._config.url,
            echo=self._config.echo,
            future=True,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False} if self._config.url.startswith("sqlite:") else {},
        )
        self._logger.debug("Database engine created", extra={"url": self._config.url})
        return engine

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        return self._session_factory

    def create_tables(self) -> None:
        """Create all database tables defined in the ORM metadata."""
        self._logger.info("Creating database tables")
        Base.metadata.create_all(self._engine)

    def drop_tables(self) -> None:
        """Drop all database tables defined in the ORM metadata."""
        self._logger.warning("Dropping database tables")
        Base.metadata.drop_all(self._engine)

    def get_session(self) -> sessionmaker[Session]:
        """Return a configured SQLAlchemy session factory."""
        return self._session_factory
