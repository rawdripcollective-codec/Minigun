"""Execution layer router: /api/v1/execution/*"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any

from minigun.api.schemas.execution import (
    CreateWorkflowRequest, WorkflowResultSchema,
    EnqueueRequest, JobSchema,
    SandboxRequest, SandboxResultSchema,
    PermissionRequest, PermissionCheckResult,
    CheckpointRequest, RollbackRequest,
    AuditRecordRequest, AuditEntrySchema,
    ApprovalRequest, ApprovalTicketSchema, ApprovalActionRequest,
)
from minigun.cognition.planner import TaskPlanner
from minigun.execution.workflow import WorkflowEngine
from minigun.execution.queue import JobQueue
from minigun.execution.sandbox import SandboxRunner
from minigun.execution.permissions import PermissionManager
from minigun.execution.rollback import RollbackManager
from minigun.execution.audit import AuditLogger
from minigun.execution.approval import ApprovalGate

router = APIRouter(prefix="/api/v1/execution", tags=["execution"])

_planner = TaskPlanner()
_workflow_engine = WorkflowEngine()
_job_queue = JobQueue()
_sandbox = SandboxRunner()
_permissions = PermissionManager()
_rollback = RollbackManager()
_audit = AuditLogger()
_approval = ApprovalGate()


# ── Workflows ──────────────────────────────────────────────────────────────
@router.post("/workflows", response_model=dict)
async def create_workflow(req: CreateWorkflowRequest) -> dict[str, Any]:
    graph = _planner.decompose(req.goal)
    wf = _workflow_engine.create_workflow(graph)
    return {"workflow_id": wf.workflow_id, "goal": wf.goal, "steps": len(wf.steps)}


@router.post("/workflows/{workflow_id}/run", response_model=WorkflowResultSchema)
async def run_workflow(workflow_id: str) -> WorkflowResultSchema:
    result = await _workflow_engine.run(workflow_id)
    return WorkflowResultSchema(
        workflow_id=result.workflow_id,
        success=result.success,
        steps_completed=result.steps_completed,
        steps_failed=result.steps_failed,
    )


# ── Jobs ───────────────────────────────────────────────────────────────────
@router.post("/jobs", response_model=dict)
async def enqueue_job(req: EnqueueRequest) -> dict[str, Any]:
    job_id = await _job_queue.enqueue(req.payload)
    return {"job_id": job_id}


@router.get("/jobs", response_model=list[JobSchema])
async def list_jobs() -> list[JobSchema]:
    return [JobSchema(job_id=j.job_id, status=j.status.value, payload=j.payload)
            for j in _job_queue.list_jobs()]


@router.get("/jobs/{job_id}", response_model=JobSchema)
async def get_job(job_id: str) -> JobSchema:
    job = _job_queue.get_job(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    return JobSchema(job_id=job.job_id, status=job.status.value, payload=job.payload)


# ── Sandbox ────────────────────────────────────────────────────────────────
@router.post("/sandbox", response_model=SandboxResultSchema)
async def run_sandbox(req: SandboxRequest) -> SandboxResultSchema:
    result = await _sandbox.run_code(req.language, req.code, req.timeout_s)  # type: ignore[arg-type]
    return SandboxResultSchema(
        language=result.language,
        success=result.success,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        timed_out=result.timed_out,
    )


# ── Permissions ────────────────────────────────────────────────────────────
@router.post("/permissions/grant", response_model=dict)
async def grant_permission(req: PermissionRequest) -> dict[str, Any]:
    _permissions.grant(req.principal, req.resource, req.action)
    return {"status": "granted"}


@router.post("/permissions/revoke", response_model=dict)
async def revoke_permission(req: PermissionRequest) -> dict[str, Any]:
    _permissions.revoke(req.principal, req.resource, req.action)
    return {"status": "revoked"}


@router.post("/permissions/check", response_model=PermissionCheckResult)
async def check_permission(req: PermissionRequest) -> PermissionCheckResult:
    allowed = _permissions.check(req.principal, req.resource, req.action)
    return PermissionCheckResult(
        principal=req.principal,
        resource=req.resource,
        action=req.action,
        allowed=allowed,
    )


# ── Rollback ───────────────────────────────────────────────────────────────
@router.post("/rollback/checkpoint", response_model=dict)
async def create_checkpoint(req: CheckpointRequest) -> dict[str, Any]:
    _rollback.checkpoint(req.label, req.state)
    return {"status": "ok", "label": req.label}


@router.post("/rollback/restore", response_model=dict)
async def restore_checkpoint(req: RollbackRequest) -> dict[str, Any]:
    state = _rollback.rollback_to(req.label)
    if state is None:
        raise HTTPException(404, f"Checkpoint '{req.label}' not found")
    return {"label": req.label, "state": state}


@router.get("/rollback/checkpoints", response_model=list[str])
async def list_checkpoints() -> list[str]:
    return _rollback.list_checkpoints()


# ── Audit ──────────────────────────────────────────────────────────────────
@router.post("/audit", response_model=AuditEntrySchema)
async def record_audit(req: AuditRecordRequest) -> AuditEntrySchema:
    entry = _audit.record(req.actor, req.action, req.resource, req.outcome, req.metadata)
    return AuditEntrySchema(
        entry_id=entry.entry_id,
        timestamp=entry.timestamp,
        actor=entry.actor,
        action=entry.action,
        resource=entry.resource,
        outcome=entry.outcome,
        metadata=entry.metadata,
    )


@router.get("/audit", response_model=list[AuditEntrySchema])
async def query_audit() -> list[AuditEntrySchema]:
    entries = _audit.query()
    return [
        AuditEntrySchema(
            entry_id=e.entry_id,
            timestamp=e.timestamp,
            actor=e.actor,
            action=e.action,
            resource=e.resource,
            outcome=e.outcome,
            metadata=e.metadata,
        )
        for e in entries
    ]


# ── Approvals ──────────────────────────────────────────────────────────────
@router.post("/approvals", response_model=ApprovalTicketSchema)
async def request_approval(req: ApprovalRequest) -> ApprovalTicketSchema:
    ticket = _approval.request_approval(req.request)
    return ApprovalTicketSchema(
        ticket_id=ticket.ticket_id,
        status=ticket.status.value,
        request=ticket.request,
    )


@router.post("/approvals/{ticket_id}/approve", response_model=ApprovalTicketSchema)
async def approve_ticket(ticket_id: str, req: ApprovalActionRequest) -> ApprovalTicketSchema:
    ticket = _approval.approve(ticket_id, req.approver)
    if not ticket:
        raise HTTPException(404, f"Ticket {ticket_id} not found")
    return ApprovalTicketSchema(
        ticket_id=ticket.ticket_id,
        status=ticket.status.value,
        request=ticket.request,
        approver=ticket.approver,
    )


@router.post("/approvals/{ticket_id}/reject", response_model=ApprovalTicketSchema)
async def reject_ticket(ticket_id: str, req: ApprovalActionRequest) -> ApprovalTicketSchema:
    ticket = _approval.reject(ticket_id, req.approver, req.reason)
    if not ticket:
        raise HTTPException(404, f"Ticket {ticket_id} not found")
    return ApprovalTicketSchema(
        ticket_id=ticket.ticket_id,
        status=ticket.status.value,
        request=ticket.request,
        approver=ticket.approver,
        rejection_reason=ticket.rejection_reason,
    )


@router.get("/approvals/{ticket_id}", response_model=ApprovalTicketSchema)
async def get_ticket(ticket_id: str) -> ApprovalTicketSchema:
    ticket = _approval.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(404, f"Ticket {ticket_id} not found")
    return ApprovalTicketSchema(
        ticket_id=ticket.ticket_id,
        status=ticket.status.value,
        request=ticket.request,
        approver=ticket.approver,
        rejection_reason=ticket.rejection_reason,
    )
