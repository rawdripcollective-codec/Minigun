"""Telemetry Service – in-memory time-series metrics store."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class TelemetryService:
    """Records and retrieves named metrics with labels."""

    def __init__(self) -> None:
        # metric_name -> list of data points
        self._store: dict[str, list[dict[str, Any]]] = {}

    def record_metric(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        if name not in self._store:
            self._store[name] = []
        point = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "value": value,
            "labels": labels or {},
        }
        self._store[name].append(point)
        logger.debug("Telemetry metric name=%s value=%s labels=%s", name, value, labels)

    def get_metrics(self, name: str) -> list[dict[str, Any]]:
        return list(self._store.get(name, []))

    def list_metric_names(self) -> list[str]:
        return list(self._store.keys())
