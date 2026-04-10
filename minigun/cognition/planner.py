"""TaskPlanner: decomposes a high-level goal into a TaskGraph."""

from __future__ import annotations

import re
from minigun.kernel.task_graph import TaskGraph, TaskNode


# Keyword → tags mapping used for heuristic decomposition
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "test": ["testing", "qa"],
    "deploy": ["deployment", "cloud"],
    "build": ["build", "ci"],
    "review": ["pr_review", "code_quality"],
    "security": ["security", "compliance"],
    "monitor": ["monitoring", "observability"],
    "document": ["documentation"],
    "refactor": ["refactor", "code_quality"],
    "database": ["database", "data"],
    "api": ["api", "backend"],
}


def _infer_tags(text: str) -> list[str]:
    text_lower = text.lower()
    tags: list[str] = []
    for kw, kw_tags in _DOMAIN_KEYWORDS.items():
        if kw in text_lower:
            tags.extend(kw_tags)
    return list(set(tags)) or ["general"]


def _estimate_tokens(description: str) -> int:
    """Rough token estimate: ~1.3 tokens per word."""
    words = len(description.split())
    return max(100, int(words * 1.3 * 10))


class TaskPlanner:
    """Decomposes a high-level goal string into a TaskGraph."""

    # Sub-task templates: (title_template, description_template, priority_offset)
    _TEMPLATES: list[tuple[str, str, int]] = [
        ("Analyse requirements", "Understand and clarify the requirements for: {goal}", 1),
        ("Design solution", "Create a high-level design addressing: {goal}", 2),
        ("Implement core logic", "Write the core implementation for: {goal}", 3),
        ("Write tests", "Create unit and integration tests for: {goal}", 4),
        ("Review & refine", "Review the solution and apply improvements for: {goal}", 5),
        ("Deploy & verify", "Deploy the solution and verify it addresses: {goal}", 6),
    ]

    def decompose(self, goal: str) -> TaskGraph:
        """Return a TaskGraph representing the decomposed goal."""
        graph = TaskGraph(goal=goal)

        previous_id: str | None = None
        for i, (title_tmpl, desc_tmpl, priority) in enumerate(self._TEMPLATES):
            title = title_tmpl
            desc = desc_tmpl.format(goal=goal)
            tags = _infer_tags(goal + " " + title)
            node = TaskNode(
                title=title,
                description=desc,
                tags=tags,
                priority=priority,
                estimated_tokens=_estimate_tokens(desc),
                dependencies=[previous_id] if previous_id else [],
            )
            graph.add_node(node)
            previous_id = node.node_id

        return graph
