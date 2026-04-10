"""UncertaintyScorer: heuristic-based uncertainty scoring for TaskNodes."""

from __future__ import annotations

from dataclasses import dataclass
from minigun.kernel.task_graph import TaskNode

_HIGH_UNCERTAINTY_TAGS = {
    "deployment", "cloud", "security", "database", "refactor",
}
_MEDIUM_UNCERTAINTY_TAGS = {"testing", "qa", "api", "backend"}


@dataclass
class UncertaintyScore:
    node_id: str
    aleatoric: float   # irreducible randomness [0-1]
    epistemic: float   # knowledge gap [0-1]
    combined: float    # combined score [0-1]


class UncertaintyScorer:
    """Returns uncertainty estimates for a TaskNode based on heuristics."""

    def score(self, node: TaskNode) -> UncertaintyScore:
        tag_set = set(node.tags)

        # Aleatoric: based on token estimate (harder tasks = more randomness)
        token_factor = min(1.0, node.estimated_tokens / 5000)

        # Epistemic: based on tag keywords indicating unknown territory
        high = len(tag_set & _HIGH_UNCERTAINTY_TAGS)
        medium = len(tag_set & _MEDIUM_UNCERTAINTY_TAGS)
        epistemic = min(1.0, high * 0.2 + medium * 0.1)

        # Dependency count adds epistemic uncertainty
        dep_factor = min(0.3, len(node.dependencies) * 0.05)
        epistemic = min(1.0, epistemic + dep_factor)

        aleatoric = round(token_factor * 0.6, 3)
        epistemic = round(epistemic, 3)
        combined = round(min(1.0, (aleatoric + epistemic) / 2 + 0.05), 3)

        return UncertaintyScore(
            node_id=node.node_id,
            aleatoric=aleatoric,
            epistemic=epistemic,
            combined=combined,
        )
