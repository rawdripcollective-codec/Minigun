"""RetrievalEngine: wraps MemoryStore and returns ranked RetrievalResult list."""

from __future__ import annotations

from dataclasses import dataclass
from minigun.cognition.memory import MemoryStore
from typing import Any


@dataclass
class RetrievalResult:
    key: str
    value: Any
    tags: list[str]
    score: float


class RetrievalEngine:
    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store or MemoryStore()

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        raw = self._store.search(query, top_k=top_k)
        return [
            RetrievalResult(
                key=r["key"],
                value=r["value"],
                tags=r["tags"],
                score=r["score"],
            )
            for r in raw
        ]

    @property
    def store(self) -> MemoryStore:
        return self._store
