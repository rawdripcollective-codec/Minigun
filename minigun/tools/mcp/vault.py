"""VaultMCP: simulated secrets management tool."""

from __future__ import annotations

from typing import Any

from minigun.tools.base import MCPTool, ToolResult
from minigun.tools.registry import ToolRegistry


class VaultMCP(MCPTool):
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    @property
    def name(self) -> str:
        return "vault"

    @property
    def description(self) -> str:
        return "Manage secrets: get, set, and list."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["get_secret", "set_secret", "list_secrets"]},
                "path": {"type": "string"},
                "value": {"type": "string"},
                "prefix": {"type": "string"},
            },
            "required": ["action"],
        }

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        action = params.get("action")
        match action:
            case "get_secret":
                path = params.get("path", "")
                value = self._store.get(path, f"<secret-value-for-{path}>")
                return ToolResult(success=True, data={"path": path, "value": value})
            case "set_secret":
                path = params.get("path", "")
                value = params.get("value", "")
                self._store[path] = value
                return ToolResult(success=True, data={"path": path, "stored": True})
            case "list_secrets":
                prefix = params.get("prefix", "")
                keys = [k for k in self._store if k.startswith(prefix)] or [
                    f"{prefix}db/password",
                    f"{prefix}api/key",
                ]
                return ToolResult(success=True, data={"prefix": prefix, "paths": keys})
        return ToolResult(success=False, error=f"Unknown action: {action}")


ToolRegistry.register(VaultMCP())
