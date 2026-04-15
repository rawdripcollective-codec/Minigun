"""Infra Solver – handles infrastructure-domain tasks."""

from __future__ import annotations

import logging
from typing import Any

from minigun.mcp.registry import MCPRegistry
from minigun.models.core import Task

logger = logging.getLogger(__name__)


class InfraSolver:
    """Executes infrastructure tasks using Terraform, Kubernetes, and Docker MCPs."""

    def __init__(self, registry: MCPRegistry | None = None) -> None:
        self._registry = registry or MCPRegistry()

    def solve(self, task: Task) -> dict[str, Any]:
        logger.info("InfraSolver solving task id=%s name=%s", task.id, task.name)
        name_lower = task.name.lower()

        if "terraform plan" in name_lower:
            result = self._registry.execute("terraform", {"action": "plan"})
            return {"status": "ok", "plan": result, "task": task.name}

        if "terraform apply" in name_lower:
            result = self._registry.execute("terraform", {"action": "apply"})
            return {"status": "ok", "apply": result, "task": task.name}

        if "kubernetes" in name_lower or "deploy" in name_lower:
            result = self._registry.execute("kubernetes", {"action": "deploy"})
            return {"status": "ok", "deploy": result, "task": task.name}

        if "health" in name_lower or "verify" in name_lower:
            result = self._registry.execute("kubernetes", {"action": "get_status"})
            return {"status": "ok", "health": result, "task": task.name}

        # Generic fallback
        return {"status": "ok", "task": task.name, "solver": "infra"}
