from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from db_copilot.config.settings import Settings, get_settings
from db_copilot.domain.models.incident import Incident
from db_copilot.mcp.client import OracleMcpClient


class BaseRule(ABC):
    """Abstract base class for all deterministic detection rules."""

    def __init__(self, mcp_client: OracleMcpClient | None = None, settings: Settings | None = None):
        self.mcp = mcp_client or OracleMcpClient()
        self.settings = settings or get_settings()

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the detection rule."""
        pass

    @abstractmethod
    async def evaluate(self, data: Any, context: dict[str, Any] | None = None) -> list[Incident]:
        """
        Evaluate input data against this rule.
        Returns a list of detected Incident domain objects.
        """
        pass
