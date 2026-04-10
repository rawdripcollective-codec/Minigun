"""DatasetMiner: mines datasets from sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatasetExample:
    input: str
    output: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Dataset:
    source: str
    examples: list[DatasetExample]
    total: int
    filters_applied: dict[str, Any]


class DatasetMiner:
    """Mines (simulates) training examples from a source."""

    def mine(self, source: str, filters: dict[str, Any] | None = None) -> Dataset:
        filters = filters or {}
        n = int(filters.get("limit", 10))
        domain = filters.get("domain", "general")
        language = filters.get("language", "python")

        examples = [
            DatasetExample(
                input=f"[{domain}] Task {i}: write a {language} function that does X_{i}",
                output=f"def x_{i}():\n    # implementation\n    pass",
                tags=[domain, language, f"example_{i}"],
                metadata={"index": i, "source": source},
            )
            for i in range(n)
        ]

        return Dataset(
            source=source,
            examples=examples,
            total=len(examples),
            filters_applied=filters,
        )
