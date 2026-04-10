"""Jira MCP – stub for issue tracking operations."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from minigun.mcp.base import MCPTool

logger = logging.getLogger(__name__)


class JiraMCP(MCPTool):
    @property
    def name(self) -> str:
        return "jira"

    @property
    def description(self) -> str:
        return "Provides Jira operations: create_issue, update_issue, get_issue."

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "get_issue")
        self._log_call(action, params)

        if action == "create_issue":
            key = f"MG-{uuid.uuid4().hex[:4].upper()}"
            return {"status": "ok", "key": key, "summary": params.get("summary", ""), "action": action}
        if action == "update_issue":
            return {"status": "ok", "key": params.get("key", "MG-0001"), "updated": True, "action": action}
        # default: get_issue
        return {
            "status": "ok",
            "key": params.get("key", "MG-0001"),
            "summary": "Sample issue",
            "status": "In Progress",
            "action": action,
        }
