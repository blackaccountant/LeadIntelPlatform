from __future__ import annotations

import abc
import logging
from typing import Any

from models import Lead


class AdapterError(Exception):
    """Raised when an adapter fails to retrieve or transform data."""


class BaseAdapter(abc.ABC):
    """Abstract base class for all data adapters."""

    def __init__(self, *, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def __enter__(self) -> "BaseAdapter":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def close(self) -> None:
        """Release any adapter-specific resources."""

    @abc.abstractmethod
    def fetch(self, *args: Any, **kwargs: Any) -> list[Lead]:
        """Fetch leads from the underlying source."""
        raise NotImplementedError
