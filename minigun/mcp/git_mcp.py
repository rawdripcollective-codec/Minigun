"""Git MCP – stub implementation for git operations."""

from __future__ import annotations

import logging
from typing import Any

from minigun.mcp.base import MCPTool

logger = logging.getLogger(__name__)

_ACTIONS = {"clone", "diff", "commit", "push", "status", "branch"}


class GitMCP(MCPTool):
    @property
    def name(self) -> str:
        return "git"

    @property
    def description(self) -> str:
        return "Provides git operations: clone, diff, commit, push, status, branch."

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "status")
        self._log_call(action, params)

        if action == "clone":
            return {"status": "ok", "path": f"/workspace/{params.get('repo', 'repo')}", "action": action}
        if action == "diff":
            return {"status": "ok", "diff": "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new", "action": action}
        if action == "commit":
            return {"status": "ok", "sha": "abc1234", "message": params.get("message", ""), "action": action}
        if action == "push":
            return {"status": "ok", "remote": params.get("remote", "origin"), "action": action}
        if action == "branch":
            return {"status": "ok", "branch": params.get("name", "main"), "action": action}
        # default: status
        return {"status": "ok", "branch": "main", "clean": True, "action": action}
