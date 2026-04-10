"""Audit router – GET /v1/audit."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from minigun.execution.audit import AuditService
from minigun.models.core import AuditEvent

router = APIRouter(prefix="/v1", tags=["audit"])
logger = logging.getLogger(__name__)

_audit = AuditService()


@router.get("/audit", response_model=list[AuditEvent])
async def list_audit_events(actor: str | None = None, action: str | None = None) -> list[AuditEvent]:
    """Return audit events, optionally filtered by actor or action."""
    filters: dict = {}
    if actor:
        filters["actor"] = actor
    if action:
        filters["action"] = action
    return _audit.list_events(filters or None)
