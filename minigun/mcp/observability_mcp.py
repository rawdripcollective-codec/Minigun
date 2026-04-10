"""Observability MCP – stub for metrics, logs, and traces."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from minigun.mcp.base import MCPTool

logger = logging.getLogger(__name__)


class ObservabilityMCP(MCPTool):
    @property
    def name(self) -> str:
        return "observability"

    @property
    def description(self) -> str:
        return "Provides observability operations: get_metrics, get_logs, get_traces."

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "get_metrics")
        self._log_call(action, params)

        now = datetime.now(timezone.utc).isoformat()
        if action == "get_metrics":
            metric = params.get("metric", "cpu_usage")
            return {
                "status": "ok",
                "metric": metric,
                "datapoints": [
                    {"timestamp": now, "value": 42.5},
                    {"timestamp": now, "value": 38.1},
                ],
                "action": action,
            }
        if action == "get_logs":
            return {
                "status": "ok",
                "service": params.get("service", "minigun"),
                "lines": ["INFO  starting up", "INFO  ready"],
                "action": action,
            }
        if action == "get_traces":
            return {
                "status": "ok",
                "trace_id": "trace-abc123",
                "spans": [{"name": "http.request", "duration_ms": 12}],
                "action": action,
            }
        return {"status": "ok", "action": action}
