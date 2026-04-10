"""Pydantic schemas for the Execution layer API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any


class CreateWorkflowRequest(BaseModel):
    goal: str


class WorkflowStepSchema(BaseModel):
    step_id: str
    node_title: str
    status: str
    output: Any = None
    error: str | None = None


class WorkflowSchema(BaseModel):
    workflow_id: str
    goal: str
    status: str
    steps: list[WorkflowStepSchema]


class WorkflowResultSchema(BaseModel):
    workflow_id: str
    success: bool
    steps_completed: int
    steps_failed: int


class EnqueueRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class JobSchema(BaseModel):
    job_id: str
    status: str
    payload: dict[str, Any]


class SandboxRequest(BaseModel):
    language: str
    code: str
    timeout_s: float = 10.0


class SandboxResultSchema(BaseModel):
    language: str
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool


class PermissionRequest(BaseModel):
    principal: str
    resource: str
    action: str


class PermissionCheckResult(BaseModel):
    principal: str
    resource: str
    action: str
    allowed: bool


class CheckpointRequest(BaseModel):
    label: str
    state: dict[str, Any]


class RollbackRequest(BaseModel):
    label: str


class AuditRecordRequest(BaseModel):
    actor: str
    action: str
    resource: str
    outcome: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditEntrySchema(BaseModel):
    entry_id: str
    timestamp: str
    actor: str
    action: str
    resource: str
    outcome: str
    metadata: dict[str, Any]


class ApprovalRequest(BaseModel):
    request: dict[str, Any]


class ApprovalTicketSchema(BaseModel):
    ticket_id: str
    status: str
    request: dict[str, Any]
    approver: str | None = None
    rejection_reason: str | None = None


class ApprovalActionRequest(BaseModel):
    approver: str
    reason: str = ""
