"""World Model Service – temporal/causal system state tracker."""

from __future__ import annotations

import logging
from typing import Any

from minigun.models.core import IncidentAlert

logger = logging.getLogger(__name__)

# Heuristic mapping of alert keywords to likely root causes
_CAUSAL_HINTS: dict[str, list[str]] = {
    "cpu": ["resource_exhaustion", "runaway_process", "insufficient_capacity"],
    "memory": ["memory_leak", "cache_bloat", "insufficient_capacity"],
    "disk": ["log_accumulation", "snapshot_backlog", "insufficient_storage"],
    "latency": ["slow_query", "network_congestion", "external_dependency_degraded"],
    "error": ["code_regression", "config_change", "dependency_failure"],
    "deploy": ["bad_artifact", "config_drift", "rollout_not_canary"],
    "crash": ["unhandled_exception", "oom_kill", "infra_failure"],
    "timeout": ["slow_query", "network_congestion", "external_dependency_degraded"],
}


class WorldModelService:
    """Maintains a temporal/causal model of the system state."""

    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    def update(self, resource: str, state: dict[str, Any]) -> None:
        """Update the known state of a resource."""
        existing = self._states.get(resource, {})
        existing.update(state)
        self._states[resource] = existing
        logger.debug("WorldModel updated resource=%s state=%s", resource, state)

    def get_state(self, resource: str) -> dict[str, Any]:
        """Return the current known state of a resource."""
        return self._states.get(resource, {})

    def correlate_incident(self, alert: IncidentAlert) -> dict[str, Any]:
        """Return likely causes for an alert based on heuristic keyword matching."""
        message_lower = alert.message.lower()
        causes: list[str] = []
        for keyword, hints in _CAUSAL_HINTS.items():
            if keyword in message_lower:
                causes.extend(hints)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_causes: list[str] = []
        for c in causes:
            if c not in seen:
                seen.add(c)
                unique_causes.append(c)

        resource_state = self.get_state(alert.source)

        return {
            "alert_id": alert.id,
            "likely_causes": unique_causes or ["unknown"],
            "resource_state": resource_state,
            "confidence": 0.7 if unique_causes else 0.2,
        }
