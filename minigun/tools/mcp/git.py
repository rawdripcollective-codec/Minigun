"""GitMCP: simulated git operations tool."""

from __future__ import annotations

from typing import Any

from minigun.tools.base import MCPTool, ToolResult
from minigun.tools.registry import ToolRegistry


class GitMCP(MCPTool):
    @property
    def name(self) -> str:
        return "git"

    @property
    def description(self) -> str:
        return "Perform git operations: clone, status, diff, commit, push."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["clone", "status", "diff", "commit", "push"],
                },
                "repo_url": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["action"],
        }

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        action = params.get("action")
        match action:
            case "clone":
                repo = params.get("repo_url", "https://github.com/example/repo.git")
                return ToolResult(
                    success=True,
                    data={"cloned_to": "/workspace/repo", "repo_url": repo, "branch": "main"},
                )
            case "status":
                return ToolResult(
                    success=True,
                    data={
                        "branch": "main",
                        "modified": ["src/main.py"],
                        "untracked": [],
                        "staged": [],
                    },
                )
            case "diff":
                return ToolResult(
                    success=True,
                    data={
                        "diff": "--- a/src/main.py\n+++ b/src/main.py\n@@ -1 +1 @@\n-old\n+new",
                        "files_changed": 1,
                    },
                )
            case "commit":
                msg = params.get("message", "chore: automated commit")
                return ToolResult(
                    success=True,
                    data={"sha": "abc1234", "message": msg, "author": "minigun-bot"},
                )
            case "push":
                return ToolResult(
                    success=True,
                    data={"remote": "origin", "branch": "main", "commits_pushed": 1},
                )
        return ToolResult(success=False, error=f"Unknown action: {action}")


ToolRegistry.register(GitMCP())
