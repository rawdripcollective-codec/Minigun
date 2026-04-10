"""MemoryStore: in-memory + optional JSON-file-backed key-value store."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MemoryStore:
    """Key-value store with tag support and keyword search."""

    def __init__(self, persist_path: str | None = None) -> None:
        self._store: dict[str, dict[str, Any]] = {}  # key → {value, tags}
        self._persist_path = Path(persist_path) if persist_path else None
        if self._persist_path and self._persist_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add(self, key: str, value: Any, tags: list[str] | None = None) -> None:
        self._store[key] = {"value": value, "tags": tags or []}
        self._save()

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            self._save()
            return True
        return False

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        return entry["value"] if entry else None

    def list_keys(self) -> list[str]:
        return list(self._store.keys())

    # ------------------------------------------------------------------
    # Search (keyword match)
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return top_k entries whose key, value string, or tags match query."""
        query_words = set(re.split(r"\W+", query.lower())) - {""}
        scored: list[tuple[float, str]] = []

        for key, entry in self._store.items():
            score = 0.0
            candidate_text = " ".join(
                [key, str(entry["value"]), " ".join(entry["tags"])]
            ).lower()
            candidate_words = set(re.split(r"\W+", candidate_text)) - {""}
            common = query_words & candidate_words
            if common:
                score = len(common) / max(len(query_words), 1)
            if score > 0:
                scored.append((score, key))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"key": k, "value": self._store[k]["value"], "tags": self._store[k]["tags"], "score": s}
            for s, k in scored[:top_k]
        ]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        if not self._persist_path:
            return
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            self._persist_path.write_text(json.dumps(self._store, indent=2))
        except OSError as exc:
            logger.warning("MemoryStore: could not save to %s: %s", self._persist_path, exc)

    def _load(self) -> None:
        try:
            data = json.loads(self._persist_path.read_text())  # type: ignore[union-attr]
            self._store = data
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("MemoryStore: could not load from %s: %s", self._persist_path, exc)
