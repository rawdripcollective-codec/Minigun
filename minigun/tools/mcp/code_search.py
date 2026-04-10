"""CodeSearchMCP: simulated code search tool."""

from __future__ import annotations

from typing import Any

from minigun.tools.base import MCPTool, ToolResult
from minigun.tools.registry import ToolRegistry


class CodeSearchMCP(MCPTool):
    @property
    def name(self) -> str:
        return "code_search"

    @property
    def description(self) -> str:
        return "Search code repositories and retrieve file contents."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["search", "get_file"]},
                "query": {"type": "string"},
                "repo": {"type": "string"},
                "top_k": {"type": "integer"},
                "path": {"type": "string"},
            },
            "required": ["action"],
        }

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        action = params.get("action")
        match action:
            case "search":
                query = params.get("query", "")
                repo = params.get("repo", "example/repo")
                top_k = params.get("top_k", 5)
                results = [
                    {
                        "file": f"src/module_{i}.py",
                        "line": i * 10 + 1,
                        "snippet": f"# matches '{query}' in module_{i}",
                        "score": round(1.0 - i * 0.1, 2),
                    }
                    for i in range(min(top_k, 5))
                ]
                return ToolResult(
                    success=True,
                    data={"repo": repo, "query": query, "results": results},
                )
            case "get_file":
                path = params.get("path", "src/main.py")
                repo = params.get("repo", "example/repo")
                return ToolResult(
                    success=True,
                    data={
                        "repo": repo,
                        "path": path,
                        "content": f"# Content of {path}\ndef main():\n    pass\n",
                        "language": "python",
                    },
                )
        return ToolResult(success=False, error=f"Unknown action: {action}")


ToolRegistry.register(CodeSearchMCP())
