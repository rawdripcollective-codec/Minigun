"""Intents router – POST /v1/intents."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from minigun.api import services
from minigun.api.routers import tasks as tasks_router
from minigun.models.core import AuditEvent, IntentRequest, TaskGraph

router = APIRouter(prefix="/v1", tags=["intents"])
logger = logging.getLogger(__name__)


@router.post("/intents", response_model=TaskGraph, status_code=201)
async def create_intent(request: IntentRequest) -> TaskGraph:
    """Accept a high-level intent and return an executed TaskGraph."""
    logger.info("Received intent: %s", request.intent)
    graph = services.planner.plan(request)
    graph = services.workflow.run(graph)
    # Register so tasks/graphs are retrievable via GET endpoints
    tasks_router.register_graph(graph)
    services.audit.record(AuditEvent(
        actor="api",
        action="create_intent",
        resource=graph.id,
        outcome="success",
        details={"intent": request.intent, "tasks": len(graph.tasks)},
    ))
    return graph
