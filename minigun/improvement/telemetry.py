"""TelemetryCollector: records and flushes telemetry events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TelemetryEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class TelemetryCollector:
    def __init__(self) -> None:
        self._events: list[TelemetryEvent] = []
        self._flushed: list[TelemetryEvent] = []

    def record_event(self, name: str, data: dict[str, Any] | None = None) -> TelemetryEvent:
        event = TelemetryEvent(name=name, data=data or {})
        self._events.append(event)
        return event

    def flush(self) -> list[TelemetryEvent]:
        batch = list(self._events)
        self._flushed.extend(batch)
        self._events.clear()
        return batch

    def summary(self) -> dict[str, Any]:
        all_events = self._events + self._flushed
        counts: dict[str, int] = {}
        for e in all_events:
            counts[e.name] = counts.get(e.name, 0) + 1
        return {
            "total_events": len(all_events),
            "unflushed": len(self._events),
            "event_counts": counts,
        }
