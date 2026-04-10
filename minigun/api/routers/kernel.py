"""Kernel router: /api/v1/kernel/run"""

from __future__ import annotations

from fastapi import APIRouter

from minigun.api.schemas.kernel import KernelRunRequest, AgentResultSchema
from minigun.kernel.agent import AgentKernel

router = APIRouter(prefix="/api/v1/kernel", tags=["kernel"])

_kernel = AgentKernel()


@router.post("/run", response_model=AgentResultSchema)
async def kernel_run(req: KernelRunRequest) -> AgentResultSchema:
    result = await _kernel.run(req.goal)
    return AgentResultSchema(
        run_id=result.run_id,
        goal=result.goal,
        intent_type=result.intent_type,
        intent_confidence=result.intent_confidence,
        plan_feasibility=result.plan_feasibility,
        plan_risk=result.plan_risk,
        workflow_id=result.workflow_id,
        steps_completed=result.steps_completed,
        steps_failed=result.steps_failed,
        success=result.success,
        critique_iterations=result.critique_iterations,
        telemetry_summary=result.telemetry_summary,
    )
