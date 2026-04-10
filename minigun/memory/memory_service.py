"""In-memory episodic and semantic memory service."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MemoryService:
    """Provides episodic (event log) and semantic (key-value) memory."""

    def __init__(self) -> None:
        self._episodic: list[dict[str, Any]] = []
        self._semantic: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Episodic memory
    # ------------------------------------------------------------------

    def store_episodic(self, event: dict[str, Any]) -> None:
        """Append an event to the episodic memory log."""
        self._episodic.append(event)
        logger.debug("Stored episodic event: %s", event)

    def recall_episodic(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """Return the k most recent events whose string repr contains the query."""
        query_lower = query.lower()
        matches = [
            e for e in self._episodic if query_lower in str(e).lower()
        ]
        # Return the k most recent matches
        return matches[-k:] if len(matches) >= k else matches

    # ------------------------------------------------------------------
    # Semantic memory
    # ------------------------------------------------------------------

    def store_semantic(self, key: str, value: dict[str, Any]) -> None:
        """Store a semantic fact under a key (upsert)."""
        self._semantic[key] = value
        logger.debug("Stored semantic memory key=%s", key)

    def recall_semantic(self, key: str) -> dict[str, Any]:
        """Retrieve a semantic fact by key; returns empty dict if not found."""
        return self._semantic.get(key, {})

    def clear(self) -> None:
        """Wipe all memory (useful for testing)."""
        self._episodic.clear()
        self._semantic.clear()
