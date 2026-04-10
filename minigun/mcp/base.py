"""Abstract base class for all MCP (Model Context Protocol) tools."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class MCPTool(ABC):
    """Base class for all MCP tool implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name used for registry lookup."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this tool does."""

    @abstractmethod
    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute the tool with the given parameters and return results."""

    def _log_call(self, action: str, params: dict[str, Any]) -> None:
        logger.info("[%s] action=%s params=%s", self.name, action, params)
