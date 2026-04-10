"""WorkflowEngine: creates and runs workflows from TaskGraphs."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from minigun.kernel.task_graph import TaskGraph, TaskNode

logger = logging.getLogger(__name__)


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    step_id: str
    node: TaskNode
    status: StepStatus = StepStatus.PENDING
    output: Any = None
    error: str | None = None


@dataclass
class Workflow:
    workflow_id: str
    goal: str
    steps: list[WorkflowStep] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    workflow_id: str
    success: bool
    steps_completed: int
    steps_failed: int
    outputs: list[Any] = field(default_factory=list)
    error: str | None = None


class WorkflowEngine:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def create_workflow(self, task_graph: TaskGraph) -> Workflow:
        wf = Workflow(
            workflow_id=str(uuid.uuid4()),
            goal=task_graph.goal,
        )
        try:
            ordered = task_graph.topological_sort()
        except Exception:
            ordered = task_graph.nodes()

        for node in ordered:
            wf.steps.append(WorkflowStep(step_id=str(uuid.uuid4()), node=node))

        self._workflows[wf.workflow_id] = wf
        return wf

    async def run(self, workflow_id: str) -> WorkflowResult:
        wf = self._workflows.get(workflow_id)
        if not wf:
            return WorkflowResult(
                workflow_id=workflow_id,
                success=False,
                steps_completed=0,
                steps_failed=0,
                error=f"Workflow {workflow_id!r} not found.",
            )

        wf.status = StepStatus.RUNNING
        completed = 0
        failed = 0
        outputs: list[Any] = []

        for step in wf.steps:
            step.status = StepStatus.RUNNING
            await asyncio.sleep(0)  # yield to event loop
            try:
                output = await self._execute_step(step)
                step.output = output
                step.status = StepStatus.COMPLETED
                outputs.append(output)
                completed += 1
            except Exception as exc:
                step.status = StepStatus.FAILED
                step.error = str(exc)
                failed += 1
                logger.warning("Step %s failed: %s", step.step_id, exc)

        wf.status = StepStatus.COMPLETED if failed == 0 else StepStatus.FAILED
        return WorkflowResult(
            workflow_id=workflow_id,
            success=failed == 0,
            steps_completed=completed,
            steps_failed=failed,
            outputs=outputs,
        )

    async def _execute_step(self, step: WorkflowStep) -> dict[str, Any]:
        """Simulate step execution."""
        await asyncio.sleep(0)
        return {
            "node_id": step.node.node_id,
            "title": step.node.title,
            "status": "completed",
        }

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)
