"""Intents router – POST /v1/intents."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from minigun.agents.planner import PlannerAgent
from minigun.execution.audit import AuditService
from minigun.execution.workflow_engine import WorkflowEngine
from minigun.models.core import AuditEvent, IntentRequest, TaskGraph

router = APIRouter(prefix="/v1", tags=["intents"])
logger = logging.getLogger(__name__)

_planner = PlannerAgent()
_workflow = WorkflowEngine()
_audit = AuditService()


@router.post("/intents", response_model=TaskGraph, status_code=201)
async def create_intent(request: IntentRequest) -> TaskGraph:
    """Accept a high-level intent and return an executed TaskGraph."""
    logger.info("Received intent: %s", request.intent)
    graph = _planner.plan(request)
    graph = _workflow.run(graph)
    _audit.record(AuditEvent(
        actor="api",
        action="create_intent",
        resource=graph.id,
        outcome="success",
        details={"intent": request.intent, "tasks": len(graph.tasks)},
    ))
    return graph
