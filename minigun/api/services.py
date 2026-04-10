"""Shared singleton service instances for API routers.

Using module-level singletons here ensures all routers share the same in-memory
state. In production these would be injected via FastAPI's Depends() backed by
a database or external service.
"""

from __future__ import annotations

from minigun.agents.planner import PlannerAgent
from minigun.execution.audit import AuditService
from minigun.execution.incident_engine import IncidentEngine
from minigun.execution.workflow_engine import WorkflowEngine

planner: PlannerAgent = PlannerAgent()
workflow: WorkflowEngine = WorkflowEngine()
audit: AuditService = AuditService()
incident_engine: IncidentEngine = IncidentEngine()
