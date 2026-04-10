"""Incident Engine – ingests alerts, correlates causes, drives remediation."""

from __future__ import annotations

import logging
from typing import Any

from minigun.agents.planner import PlannerAgent
from minigun.memory.world_model import WorldModelService
from minigun.models.core import IncidentAlert, IntentRequest, TaskGraph

logger = logging.getLogger(__name__)


class IncidentEngine:
    """Ingests incident alerts and drives automated remediation."""

    def __init__(
        self,
        world_model: WorldModelService | None = None,
        planner: PlannerAgent | None = None,
    ) -> None:
        self._world_model = world_model or WorldModelService()
        self._planner = planner or PlannerAgent()
        self._alerts: dict[str, IncidentAlert] = {}
        self._correlations: dict[str, dict[str, Any]] = {}

    def ingest(self, alert: IncidentAlert) -> None:
        """Store the alert and correlate it with the world model."""
        self._alerts[alert.id] = alert
        correlation = self._world_model.correlate_incident(alert)
        self._correlations[alert.id] = correlation
        logger.info(
            "Incident ingested id=%s severity=%s causes=%s",
            alert.id,
            alert.severity,
            correlation.get("likely_causes"),
        )

    def create_remediation_graph(self, alert: IncidentAlert) -> TaskGraph:
        """Create a TaskGraph to remediate the given alert."""
        if alert.id not in self._alerts:
            self.ingest(alert)

        correlation = self._correlations.get(alert.id, {})
        intent = (
            f"Remediate incident: {alert.message}. "
            f"Severity: {alert.severity}. "
            f"Likely causes: {', '.join(correlation.get('likely_causes', ['unknown']))}."
        )
        intent_request = IntentRequest(
            intent=intent,
            context={
                "alert_id": alert.id,
                "source": alert.source,
                "severity": alert.severity,
                "metadata": alert.metadata,
            },
            priority="critical" if alert.severity in ("P1", "P2") else "high",
        )
        graph = self._planner.plan(intent_request)
        logger.info("Remediation graph id=%s for alert id=%s", graph.id, alert.id)
        return graph

    def generate_postmortem(self, incident_id: str) -> dict[str, Any]:
        """Return a structured postmortem document for a past incident."""
        alert = self._alerts.get(incident_id)
        if alert is None:
            return {"error": f"Incident '{incident_id}' not found"}

        correlation = self._correlations.get(incident_id, {})
        return {
            "incident_id": incident_id,
            "severity": alert.severity,
            "source": alert.source,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "likely_causes": correlation.get("likely_causes", []),
            "confidence": correlation.get("confidence", 0.0),
            "timeline": [
                {"phase": "detection", "description": f"Alert received from {alert.source}"},
                {"phase": "triage", "description": "Incident triaged by SRE Solver"},
                {"phase": "remediation", "description": "Remediation TaskGraph executed"},
                {"phase": "recovery", "description": "System recovery verified"},
            ],
            "action_items": [
                "Add monitoring for early detection",
                "Update runbooks with remediation steps",
                "Review risk controls for similar incidents",
            ],
        }
