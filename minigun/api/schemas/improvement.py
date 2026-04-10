"""Pydantic schemas for the Improvement layer API."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class EvaluateRequest(BaseModel):
    task_run: dict[str, Any]


class EvalResultSchema(BaseModel):
    score: float
    breakdown: dict[str, float]
    notes: list[str]


class TelemetryEventRequest(BaseModel):
    name: str
    data: dict[str, Any] = Field(default_factory=dict)


class TelemetryEventSchema(BaseModel):
    event_id: str
    name: str
    data: dict[str, Any]
    timestamp: str


class TelemetrySummarySchema(BaseModel):
    total_events: int
    unflushed: int
    event_counts: dict[str, int]


class DatasetMineRequest(BaseModel):
    source: str
    filters: dict[str, Any] = Field(default_factory=dict)


class DatasetExampleSchema(BaseModel):
    input: str
    output: str
    tags: list[str]
    metadata: dict[str, Any]


class DatasetSchema(BaseModel):
    source: str
    examples: list[DatasetExampleSchema]
    total: int
    filters_applied: dict[str, Any]


class RewardScoreRequest(BaseModel):
    trajectory: list[dict[str, Any]]


class RewardScoreSchema(BaseModel):
    score: float


class SyntheticRequest(BaseModel):
    domain: str
    n: int = 5


class SyntheticTaskSchema(BaseModel):
    task_id: str
    domain: str
    description: str
    expected_output_hint: str
    difficulty: str
    tags: list[str]


class RefreshScheduleRequest(BaseModel):
    model_id: str
    dataset_id: str
    params: dict[str, Any] = Field(default_factory=dict)


class RefreshJobSchema(BaseModel):
    refresh_id: str
    model_id: str
    dataset_id: str
    status: str
    created_at: str
    finished_at: str | None = None
