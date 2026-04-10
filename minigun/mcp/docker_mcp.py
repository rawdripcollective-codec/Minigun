"""Docker MCP – stub implementation for container operations."""

from __future__ import annotations

import logging
from typing import Any

from minigun.mcp.base import MCPTool

logger = logging.getLogger(__name__)


class DockerMCP(MCPTool):
    @property
    def name(self) -> str:
        return "docker"

    @property
    def description(self) -> str:
        return "Provides Docker operations: build, run, stop, inspect."

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "inspect")
        self._log_call(action, params)

        if action == "build":
            image = params.get("image", "minigun:latest")
            return {"status": "ok", "image": image, "size_mb": 120, "action": action}
        if action == "run":
            return {"status": "ok", "container_id": "c0ffee1234ab", "image": params.get("image", ""), "action": action}
        if action == "stop":
            return {"status": "ok", "container_id": params.get("container_id", ""), "action": action}
        # default: inspect
        return {
            "status": "ok",
            "container_id": params.get("container_id", "c0ffee1234ab"),
            "state": "running",
            "action": action,
        }
