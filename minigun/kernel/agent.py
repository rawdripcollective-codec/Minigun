"""AgentKernel: the central orchestrator."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from minigun.cognition.intent import IntentInferencer
from minigun.cognition.planner import TaskPlanner
from minigun.cognition.critic import PlanCritic
from minigun.execution.workflow import WorkflowEngine
from minigun.improvement.telemetry import TelemetryCollector
from minigun.kernel.task_graph import TaskGraph

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    run_id: str
    goal: str
    intent_type: str
    intent_confidence: float
    plan_feasibility: float
    plan_risk: float
    workflow_id: str
    steps_completed: int
    steps_failed: int
    success: bool
    critique_iterations: int
    telemetry_summary: dict[str, Any] = field(default_factory=dict)


class AgentKernel:
    """Central orchestrator: infer intent → plan → critique → execute."""

    MAX_CRITIQUE_LOOPS = 3

    def __init__(self) -> None:
        self._intent_inferencer = IntentInferencer()
        self._planner = TaskPlanner()
        self._critic = PlanCritic()
        self._workflow_engine = WorkflowEngine()
        self._telemetry = TelemetryCollector()

    async def run(self, goal: str) -> AgentResult:
        run_id = str(uuid.uuid4())
        logger.info("AgentKernel.run [%s]: %s", run_id, goal)
        self._telemetry.record_event("kernel.run.start", {"run_id": run_id, "goal": goal})

        # 1. Infer intent
        intent = self._intent_inferencer.infer(goal)
        self._telemetry.record_event(
            "kernel.intent", {"type": intent.intent_type, "confidence": intent.confidence}
        )

        # 2. Plan
        graph: TaskGraph = self._planner.decompose(goal)
        self._telemetry.record_event("kernel.plan", {"nodes": len(graph)})

        # 3. Critique loop (up to MAX_CRITIQUE_LOOPS)
        critique_iterations = 0
        report = None
        for _ in range(self.MAX_CRITIQUE_LOOPS):
            critique_iterations += 1
            report = self._critic.critique(graph)
            self._telemetry.record_event(
                "kernel.critique",
                {"feasibility": report.feasibility, "risk": report.risk},
            )
            if report.feasibility >= 0.5 and report.risk <= 0.7:
                break
            # Attempt to re-plan if plan is poor (simplified: just use the same graph)
            logger.debug("Re-planning due to low feasibility or high risk.")

        # 4. Execute via WorkflowEngine
        workflow = self._workflow_engine.create_workflow(graph)
        wf_result = await self._workflow_engine.run(workflow.workflow_id)
        self._telemetry.record_event(
            "kernel.execution",
            {
                "workflow_id": workflow.workflow_id,
                "completed": wf_result.steps_completed,
                "failed": wf_result.steps_failed,
            },
        )

        # 5. Record telemetry
        self._telemetry.record_event("kernel.run.end", {"success": wf_result.success})
        summary = self._telemetry.summary()

        return AgentResult(
            run_id=run_id,
            goal=goal,
            intent_type=intent.intent_type,
            intent_confidence=intent.confidence,
            plan_feasibility=report.feasibility if report else 0.0,
            plan_risk=report.risk if report else 1.0,
            workflow_id=workflow.workflow_id,
            steps_completed=wf_result.steps_completed,
            steps_failed=wf_result.steps_failed,
            success=wf_result.success,
            critique_iterations=critique_iterations,
            telemetry_summary=summary,
        )
