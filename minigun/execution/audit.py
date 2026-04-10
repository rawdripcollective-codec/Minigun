"""Audit Service – immutable append-only log of platform events."""

from __future__ import annotations

import logging
from typing import Any

from minigun.models.core import AuditEvent

logger = logging.getLogger(__name__)


class AuditService:
    """In-memory audit log."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self._events.append(event)
        logger.info("Audit event id=%s actor=%s action=%s resource=%s outcome=%s",
                    event.id, event.actor, event.action, event.resource, event.outcome)

    def list_events(self, filters: dict[str, Any] | None = None) -> list[AuditEvent]:
        """Return events matching all provided filter key=value pairs."""
        if not filters:
            return list(self._events)
        result: list[AuditEvent] = []
        for event in self._events:
            if all(getattr(event, k, None) == v for k, v in filters.items()):
                result.append(event)
        return result
