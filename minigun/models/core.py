"""Core Pydantic models shared across the platform."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


# ---------------------------------------------------------------------------
# Core request / graph models
# ---------------------------------------------------------------------------


class IntentRequest(BaseModel):
    id: str = Field(default_factory=_new_id)
    intent: str
    context: dict[str, Any] = Field(default_factory=dict)
    priority: str = Priority.MEDIUM
    created_at: datetime = Field(default_factory=_now)


class Task(BaseModel):
    id: str = Field(default_factory=_new_id)
    name: str
    type: str  # e.g. "code", "infra", "sre", "data"
    status: TaskStatus = TaskStatus.PENDING
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    assigned_solver: str = ""
    dependencies: list[str] = Field(default_factory=list)
    retries: int = 0
    error: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class TaskGraph(BaseModel):
    id: str = Field(default_factory=_new_id)
    intent: str
    tasks: list[Task] = Field(default_factory=list)
    # edges: list of (from_task_id, to_task_id)
    edges: list[tuple[str, str]] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Verification / Risk / Audit
# ---------------------------------------------------------------------------


class VerificationResult(BaseModel):
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=_now)


class RiskScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    level: str = RiskLevel.LOW
    factors: list[str] = Field(default_factory=list)
    requires_approval: bool = False


class AuditEvent(BaseModel):
    id: str = Field(default_factory=_new_id)
    timestamp: datetime = Field(default_factory=_now)
    actor: str
    action: str
    resource: str
    outcome: str  # "success" | "failure" | "pending"
    details: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------


class IncidentAlert(BaseModel):
    id: str = Field(default_factory=_new_id)
    severity: str = Severity.P3
    source: str
    message: str
    timestamp: datetime = Field(default_factory=_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Eval
# ---------------------------------------------------------------------------


class EvalResult(BaseModel):
    run_id: str = Field(default_factory=_new_id)
    task_id: str
    score: float = Field(ge=0.0, le=1.0)
    metrics: dict[str, float] = Field(default_factory=dict)
    passed: bool
    evaluated_at: datetime = Field(default_factory=_now)
