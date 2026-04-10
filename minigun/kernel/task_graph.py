"""Task graph primitives: TaskNode and TaskGraph (DAG)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskNode:
    """A single unit of work within a TaskGraph."""

    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    priority: int = 5  # 1 (highest) – 10 (lowest)
    estimated_tokens: int = 500
    dependencies: list[str] = field(default_factory=list)  # node_ids
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id:
            self.node_id = str(uuid.uuid4())


class CycleError(Exception):
    """Raised when a cycle is detected in the task graph."""


class TaskGraph:
    """Directed Acyclic Graph of TaskNodes."""

    def __init__(self, goal: str = "") -> None:
        self.graph_id: str = str(uuid.uuid4())
        self.goal: str = goal
        self._nodes: dict[str, TaskNode] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_node(self, node: TaskNode) -> None:
        self._nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)
        for n in self._nodes.values():
            if node_id in n.dependencies:
                n.dependencies.remove(node_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> TaskNode | None:
        return self._nodes.get(node_id)

    def nodes(self) -> list[TaskNode]:
        return list(self._nodes.values())

    def __len__(self) -> int:
        return len(self._nodes)

    # ------------------------------------------------------------------
    # Algorithms
    # ------------------------------------------------------------------

    def has_cycle(self) -> bool:
        """Return True if the graph contains a cycle."""
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(nid: str) -> bool:
            visited.add(nid)
            rec_stack.add(nid)
            node = self._nodes.get(nid)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        if dfs(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            rec_stack.discard(nid)
            return False

        for node_id in self._nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        return False

    def topological_sort(self) -> list[TaskNode]:
        """Return nodes in topological order (dependencies first).

        Raises CycleError if a cycle is detected.
        """
        if self.has_cycle():
            raise CycleError("Task graph contains a cycle")

        in_degree: dict[str, int] = {nid: 0 for nid in self._nodes}
        # Build adjacency: dependency → dependents
        dependents: dict[str, list[str]] = {nid: [] for nid in self._nodes}

        for nid, node in self._nodes.items():
            for dep in node.dependencies:
                if dep in self._nodes:
                    in_degree[nid] += 1
                    dependents[dep].append(nid)

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order: list[TaskNode] = []

        while queue:
            queue.sort(key=lambda nid: self._nodes[nid].priority)
            nid = queue.pop(0)
            order.append(self._nodes[nid])
            for dependent in dependents.get(nid, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return order
