"""SpecialisedExecutor: routes TaskNodes to the right App or MCP tool."""

from __future__ import annotations

import asyncio
from typing import Any

from minigun.kernel.task_graph import TaskNode
from minigun.tools.registry import ToolRegistry


# Tag → app factory mapping (lazy import to avoid circular deps)
_TAG_TO_APP: dict[str, str] = {
    "codegen": "codegen",
    "testing": "testing",
    "qa": "testing",
    "pr_review": "pr_review",
    "code_quality": "pr_review",
    "deployment": "cloud",
    "cloud": "cloud",
    "security": "compliance",
    "compliance": "compliance",
    "documentation": "codegen",
}

_TAG_TO_TOOL: dict[str, str] = {
    "git": "git",
    "browser": "browser",
    "vault": "vault",
    "code_search": "code_search",
    "cloud": "cloud",
    "deployment": "cloud",
}


async def _run_app(app_name: str, node: TaskNode) -> dict[str, Any]:
    """Import and run the appropriate app for the node."""
    if app_name == "codegen":
        from minigun.apps.codegen import CodegenApp, CodegenSpec
        app = CodegenApp()
        spec = CodegenSpec(language="python", description=node.description)
        result = app.generate(spec)
        return {"app": app_name, "code": result.code[:200], "warnings": result.warnings}

    elif app_name == "testing":
        from minigun.apps.testing import TestingApp
        app = TestingApp()
        suite = app.generate_tests(node.description, "python")
        return {"app": app_name, "framework": suite.framework, "test_count": len(suite.test_cases)}

    elif app_name == "pr_review":
        from minigun.apps.pr_review import PRReviewApp
        app = PRReviewApp()
        report = app.review(node.description)
        return {"app": app_name, "risk": report.risk_level, "issue_count": len(report.issues)}

    elif app_name in ("cloud", "deployment"):
        result = await ToolRegistry.execute("cloud", {"action": "list_resources", "service": "compute"})
        return {"app": app_name, "tool_result": result.data}

    elif app_name == "compliance":
        from minigun.apps.compliance import ComplianceApp
        app = ComplianceApp()
        report = app.check(node.description, ["OWASP"])
        return {"app": app_name, "status": report.overall_status}

    return {"app": app_name, "status": "simulated", "node_id": node.node_id}


class SpecialisedExecutor:
    """Routes a TaskNode to the right App or MCP tool and executes it."""

    async def execute(self, node: TaskNode) -> dict[str, Any]:
        tag_set = set(node.tags)

        # Check tool tags first
        for tag, tool_name in _TAG_TO_TOOL.items():
            if tag in tag_set:
                action_map = {
                    "git": {"action": "status"},
                    "browser": {"action": "navigate", "url": "https://example.com"},
                    "vault": {"action": "list_secrets", "prefix": ""},
                    "code_search": {"action": "search", "query": node.title},
                    "cloud": {"action": "list_resources", "service": "compute"},
                }
                result = await ToolRegistry.execute(tool_name, action_map.get(tool_name, {}))
                return {"tool": tool_name, "success": result.success, "data": result.data}

        # Check app tags
        for tag, app_name in _TAG_TO_APP.items():
            if tag in tag_set:
                return await _run_app(app_name, node)

        # Default: simulate generic execution
        await asyncio.sleep(0)
        return {"status": "completed", "node_id": node.node_id, "title": node.title}
