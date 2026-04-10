"""Incidents router – POST /v1/incidents."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from minigun.execution.incident_engine import IncidentEngine
from minigun.models.core import IncidentAlert, TaskGraph

router = APIRouter(prefix="/v1", tags=["incidents"])
logger = logging.getLogger(__name__)

_incident_engine = IncidentEngine()


@router.post("/incidents", response_model=TaskGraph, status_code=201)
async def create_incident(alert: IncidentAlert) -> TaskGraph:
    """Ingest an incident alert and return a remediation TaskGraph."""
    logger.info("Incident received id=%s severity=%s", alert.id, alert.severity)
    _incident_engine.ingest(alert)
    graph = _incident_engine.create_remediation_graph(alert)
    return graph
