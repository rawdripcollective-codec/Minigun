"""ToolRegistry: singleton registry for MCP tools."""

from __future__ import annotations

import logging
from typing import Any

from minigun.tools.base import MCPTool, ToolResult

logger = logging.getLogger(__name__)


class _ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s", tool.name)

    def get(self, name: str) -> MCPTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {"name": t.name, "description": t.description, "schema": t.schema}
            for t in self._tools.values()
        ]

    async def execute(self, name: str, params: dict[str, Any]) -> ToolResult:
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(success=False, error=f"Tool '{name}' not found.")
        return await tool.execute(params)


# Singleton instance
ToolRegistry = _ToolRegistry()
