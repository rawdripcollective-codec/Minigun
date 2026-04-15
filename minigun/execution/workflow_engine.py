"""Workflow Engine – executes a TaskGraph respecting dependencies with retry logic."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from minigun.agents.solvers import CodeSolver, DataSolver, InfraSolver, SRESolver
from minigun.config import settings
from minigun.models.core import Task, TaskGraph, TaskStatus

logger = logging.getLogger(__name__)

_BACKOFF_BASE: float = 1.0  # seconds; doubled on each retry


def _now() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowEngine:
    """Runs a TaskGraph by executing tasks in dependency order with retries."""

    def __init__(self) -> None:
        self._solvers: dict[str, Any] = {
            "code": CodeSolver(),
            "infra": InfraSolver(),
            "data": DataSolver(),
            "sre": SRESolver(),
        }

    def _get_solver(self, solver_name: str):
        solver = self._solvers.get(solver_name)
        if solver is None:
            raise ValueError(f"No solver registered for '{solver_name}'")
        return solver

    def _can_run(self, task: Task, completed_ids: set[str]) -> bool:
        """Return True if all dependencies are satisfied."""
        return all(dep in completed_ids for dep in task.dependencies)

    def _execute_task(self, task: Task) -> dict[str, Any]:
        """Execute a single task with exponential-backoff retry logic."""
        solver = self._get_solver(task.assigned_solver)
        last_error: Exception | None = None

        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                result = solver.solve(task)
                return result
            except Exception as exc:
                last_error = exc
                task.retries = attempt
                logger.warning(
                    "Task id=%s attempt=%d/%d failed: %s",
                    task.id,
                    attempt,
                    settings.MAX_RETRIES,
                    exc,
                )
                if attempt < settings.MAX_RETRIES:
                    backoff = _BACKOFF_BASE * (2 ** (attempt - 1))
                    logger.debug("Backing off %.1fs before retry", backoff)
                    time.sleep(backoff)

        raise RuntimeError(f"Task '{task.name}' failed after {settings.MAX_RETRIES} retries") from last_error

    def run(self, graph: TaskGraph) -> TaskGraph:
        """Execute all tasks in the graph, respecting dependency order."""
        logger.info("WorkflowEngine starting graph id=%s tasks=%d", graph.id, len(graph.tasks))

        graph.status = TaskStatus.RUNNING
        graph.updated_at = _now()

        tasks_by_id: dict[str, Task] = {t.id: t for t in graph.tasks}
        completed_ids: set[str] = set()
        # Use a simple iterative topological pass
        remaining = list(graph.tasks)

        while remaining:
            progress = False
            for task in list(remaining):
                if not self._can_run(task, completed_ids):
                    continue

                task.status = TaskStatus.RUNNING
                task.updated_at = _now()

                try:
                    result = self._execute_task(task)
                    task.outputs = result
                    task.status = TaskStatus.COMPLETED
                    completed_ids.add(task.id)
                    logger.info("Task completed id=%s name=%s", task.id, task.name)
                except Exception as exc:
                    task.status = TaskStatus.FAILED
                    task.error = str(exc)
                    logger.error("Task failed id=%s name=%s error=%s", task.id, task.name, exc)
                    # Mark dependents as SKIPPED
                    self._skip_dependents(task, tasks_by_id, completed_ids)

                task.updated_at = _now()
                remaining.remove(task)
                progress = True

            if not progress:
                # Circular dependencies or all remaining tasks blocked – skip them
                for task in remaining:
                    task.status = TaskStatus.SKIPPED
                    task.updated_at = _now()
                break

        all_statuses = {t.status for t in graph.tasks}
        if TaskStatus.FAILED in all_statuses:
            graph.status = TaskStatus.FAILED
        elif all_statuses <= {TaskStatus.COMPLETED, TaskStatus.SKIPPED}:
            graph.status = TaskStatus.COMPLETED
        else:
            graph.status = TaskStatus.COMPLETED

        graph.updated_at = _now()
        logger.info("Graph id=%s finished with status=%s", graph.id, graph.status)
        return graph

    def _skip_dependents(
        self,
        failed_task: Task,
        tasks_by_id: dict[str, Task],
        completed_ids: set[str],
    ) -> None:
        """Mark all transitive dependents of a failed task as SKIPPED."""
        for task in tasks_by_id.values():
            if failed_task.id in task.dependencies and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.SKIPPED
                task.updated_at = _now()
                completed_ids.add(task.id)  # treat as resolved so loop doesn't stall
                self._skip_dependents(task, tasks_by_id, completed_ids)
