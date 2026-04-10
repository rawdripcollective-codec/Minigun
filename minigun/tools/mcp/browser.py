"""BrowserMCP: simulated browser navigation tool."""

from __future__ import annotations

from typing import Any

from minigun.tools.base import MCPTool, ToolResult
from minigun.tools.registry import ToolRegistry


class BrowserMCP(MCPTool):
    @property
    def name(self) -> str:
        return "browser"

    @property
    def description(self) -> str:
        return "Navigate web pages, take screenshots, and extract text."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["navigate", "screenshot", "extract_text"]},
                "url": {"type": "string"},
                "selector": {"type": "string"},
            },
            "required": ["action"],
        }

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        action = params.get("action")
        if action == "navigate":
            url = params.get("url", "https://example.com")
            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "status_code": 200,
                    "title": f"Page at {url}",
                    "content_length": 4096,
                },
            )
        elif action == "screenshot":
            return ToolResult(
                success=True,
                data={"format": "png", "width": 1280, "height": 800, "base64": "iVBORw0KGgo="},
            )
        elif action == "extract_text":
            selector = params.get("selector", "body")
            return ToolResult(
                success=True,
                data={"selector": selector, "text": f"Extracted text from '{selector}'"},
            )
        return ToolResult(success=False, error=f"Unknown action: {action}")


# Auto-register
ToolRegistry.register(BrowserMCP())
