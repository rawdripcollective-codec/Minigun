"""MCP Registry – central lookup for all registered tools."""

from __future__ import annotations

import logging
from typing import Any

from minigun.mcp.base import MCPTool
from minigun.mcp.docker_mcp import DockerMCP
from minigun.mcp.git_mcp import GitMCP
from minigun.mcp.jira_mcp import JiraMCP
from minigun.mcp.kubernetes_mcp import KubernetesMCP
from minigun.mcp.observability_mcp import ObservabilityMCP
from minigun.mcp.security_mcp import SecurityMCP
from minigun.mcp.slack_mcp import SlackMCP
from minigun.mcp.terraform_mcp import TerraformMCP

logger = logging.getLogger(__name__)


class MCPRegistry:
    """Registers and looks up MCP tools by name."""

    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults: list[MCPTool] = [
            GitMCP(),
            DockerMCP(),
            KubernetesMCP(),
            TerraformMCP(),
            ObservabilityMCP(),
            SecurityMCP(),
            JiraMCP(),
            SlackMCP(),
        ]
        for tool in defaults:
            self.register(tool)

    def register(self, tool: MCPTool) -> None:
        logger.debug("Registering MCP tool: %s", tool.name)
        self._tools[tool.name] = tool

    def get(self, name: str) -> MCPTool:
        if name not in self._tools:
            raise KeyError(f"MCP tool '{name}' is not registered")
        return self._tools[name]

    def execute(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        return self.get(tool_name).execute(params)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
