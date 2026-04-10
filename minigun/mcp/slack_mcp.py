"""Slack MCP – stub for messaging operations."""

from __future__ import annotations

import logging
from typing import Any

from minigun.mcp.base import MCPTool

logger = logging.getLogger(__name__)


class SlackMCP(MCPTool):
    @property
    def name(self) -> str:
        return "slack"

    @property
    def description(self) -> str:
        return "Provides Slack operations: send_message, create_channel."

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "send_message")
        self._log_call(action, params)

        if action == "send_message":
            return {
                "status": "ok",
                "channel": params.get("channel", "#general"),
                "ts": "1700000000.000001",
                "action": action,
            }
        if action == "create_channel":
            return {"status": "ok", "channel": params.get("name", "minigun-ops"), "action": action}
        return {"status": "ok", "action": action}
