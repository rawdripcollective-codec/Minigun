"""PlanCritic: scores a TaskGraph and returns a CritiqueReport."""

from __future__ import annotations

from dataclasses import dataclass, field
from minigun.kernel.task_graph import TaskGraph


@dataclass
class CritiqueReport:
    feasibility: float  # 0-1
    risk: float  # 0-1
    recommendations: list[str] = field(default_factory=list)
    notes: str = ""


class PlanCritic:
    """Scores a TaskGraph on feasibility and risk."""

    _HIGH_RISK_TAGS = {"deployment", "cloud", "security", "database"}
    _COMPLEXITY_THRESHOLD = 10  # number of nodes

    def critique(self, graph: TaskGraph) -> CritiqueReport:
        nodes = graph.nodes()
        if not nodes:
            return CritiqueReport(
                feasibility=0.0,
                risk=1.0,
                recommendations=["Graph is empty – add at least one task node."],
                notes="Empty graph cannot be executed.",
            )

        n = len(nodes)
        recommendations: list[str] = []

        # Feasibility heuristic: decreases with very large graphs or cycles
        has_cycle = graph.has_cycle()
        if has_cycle:
            feasibility = 0.1
            recommendations.append("Graph contains a cycle – remove circular dependencies.")
        else:
            feasibility = max(0.4, 1.0 - (n - 1) * 0.05)

        # Risk heuristic: increases with high-risk tags and token estimates
        all_tags: set[str] = set()
        total_tokens = 0
        for node in nodes:
            all_tags.update(node.tags)
            total_tokens += node.estimated_tokens

        risk_tags = all_tags & self._HIGH_RISK_TAGS
        risk = min(1.0, len(risk_tags) * 0.15 + (total_tokens / 50_000))

        if risk_tags:
            recommendations.append(
                f"High-risk domains detected: {', '.join(sorted(risk_tags))}."
                " Consider adding approval gates."
            )

        if n > self._COMPLEXITY_THRESHOLD:
            recommendations.append(
                f"Graph has {n} nodes which may be overly complex."
                " Consider splitting into sub-graphs."
            )

        avg_tokens = total_tokens / n
        if avg_tokens > 2000:
            recommendations.append(
                "Average token estimate per node is high."
                " Consider breaking large nodes into smaller ones."
            )

        if not recommendations:
            recommendations.append("Plan looks healthy – no critical issues detected.")

        return CritiqueReport(
            feasibility=round(feasibility, 3),
            risk=round(min(risk, 1.0), 3),
            recommendations=recommendations,
            notes=f"Evaluated {n} nodes; total estimated tokens: {total_tokens}.",
        )
