"""Terraform MCP – stub implementation for IaC operations."""

from __future__ import annotations

import logging
from typing import Any

from minigun.mcp.base import MCPTool

logger = logging.getLogger(__name__)


class TerraformMCP(MCPTool):
    @property
    def name(self) -> str:
        return "terraform"

    @property
    def description(self) -> str:
        return "Provides Terraform operations: plan, apply, destroy."

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "plan")
        self._log_call(action, params)

        workspace = params.get("workspace", "default")
        if action == "plan":
            return {"status": "ok", "workspace": workspace, "changes": {"add": 2, "change": 1, "destroy": 0}, "action": action}
        if action == "apply":
            return {"status": "ok", "workspace": workspace, "applied": True, "resources_created": 2, "action": action}
        if action == "destroy":
            return {"status": "ok", "workspace": workspace, "destroyed": True, "action": action}
        return {"status": "ok", "workspace": workspace, "action": action}
