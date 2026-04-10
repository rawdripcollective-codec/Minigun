"""Pydantic schemas for the AgentKernel API."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class KernelRunRequest(BaseModel):
    goal: str = Field(..., min_length=1)


class AgentResultSchema(BaseModel):
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
    telemetry_summary: dict[str, Any] = Field(default_factory=dict)


class ToolListSchema(BaseModel):
    name: str
    description: str
    schema_def: dict[str, Any] = Field(alias="schema")

    model_config = {"populate_by_name": True}


class ToolExecuteRequest(BaseModel):
    name: str
    params: dict[str, Any] = Field(default_factory=dict)


class ToolResultSchema(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
