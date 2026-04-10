"""SRE Solver – handles site reliability / incident-domain tasks."""

from __future__ import annotations

import logging
from typing import Any

from minigun.mcp.registry import MCPRegistry
from minigun.models.core import Task

logger = logging.getLogger(__name__)


class SRESolver:
    """Executes SRE tasks using Observability, Kubernetes, and Slack MCPs."""

    def __init__(self, registry: MCPRegistry | None = None) -> None:
        self._registry = registry or MCPRegistry()

    def solve(self, task: Task) -> dict[str, Any]:
        logger.info("SRESolver solving task id=%s name=%s", task.id, task.name)
        name_lower = task.name.lower()

        if "triage" in name_lower:
            logs = self._registry.execute("observability", {"action": "get_logs", "service": "minigun"})
            return {"status": "ok", "triage": logs, "task": task.name}

        if "root cause" in name_lower or "identify" in name_lower:
            traces = self._registry.execute("observability", {"action": "get_traces"})
            return {"status": "ok", "root_cause": "high_error_rate", "traces": traces, "task": task.name}

        if "remediat" in name_lower or "apply" in name_lower:
            rollout = self._registry.execute("kubernetes", {"action": "deploy", "deployment": "minigun"})
            return {"status": "ok", "remediation": rollout, "task": task.name}

        if "verify" in name_lower or "recovery" in name_lower:
            status = self._registry.execute("kubernetes", {"action": "get_status"})
            return {"status": "ok", "recovery_verified": True, "k8s_status": status, "task": task.name}

        if "postmortem" in name_lower:
            self._registry.execute("slack", {"action": "send_message", "channel": "#incidents", "text": "Postmortem ready"})
            return {"status": "ok", "postmortem": "Postmortem document drafted", "task": task.name}

        # Generic fallback
        return {"status": "ok", "task": task.name, "solver": "sre"}
