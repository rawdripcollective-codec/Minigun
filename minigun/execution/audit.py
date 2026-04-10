"""AuditLogger: append-only audit log."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AuditEntry:
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    actor: str = ""
    action: str = ""
    resource: str = ""
    outcome: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class AuditLogger:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(
        self,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        return entry

    def query(self, filters: dict[str, str] | None = None) -> list[AuditEntry]:
        if not filters:
            return list(self._entries)
        result = []
        for e in self._entries:
            match = all(
                getattr(e, k, None) == v for k, v in filters.items()
            )
            if match:
                result.append(e)
        return result
