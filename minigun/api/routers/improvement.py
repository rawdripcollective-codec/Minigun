"""Improvement layer router: /api/v1/improvement/*"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any

from minigun.api.schemas.improvement import (
    EvaluateRequest, EvalResultSchema,
    TelemetryEventRequest, TelemetryEventSchema, TelemetrySummarySchema,
    DatasetMineRequest, DatasetSchema, DatasetExampleSchema,
    RewardScoreRequest, RewardScoreSchema,
    SyntheticRequest, SyntheticTaskSchema,
    RefreshScheduleRequest, RefreshJobSchema,
)
from minigun.improvement.evaluation import OfflineEvaluator
from minigun.improvement.telemetry import TelemetryCollector
from minigun.improvement.dataset import DatasetMiner
from minigun.improvement.reward import RewardModel
from minigun.improvement.synthetic import SyntheticTaskGenerator
from minigun.improvement.refresh import ModelRefreshController

router = APIRouter(prefix="/api/v1/improvement", tags=["improvement"])

_evaluator = OfflineEvaluator()
_telemetry = TelemetryCollector()
_dataset_miner = DatasetMiner()
_reward = RewardModel()
_synthetic = SyntheticTaskGenerator()
_refresh = ModelRefreshController()


@router.post("/evaluate", response_model=EvalResultSchema)
async def evaluate(req: EvaluateRequest) -> EvalResultSchema:
    result = _evaluator.evaluate(req.task_run)
    return EvalResultSchema(score=result.score, breakdown=result.breakdown, notes=result.notes)


@router.post("/telemetry/event", response_model=TelemetryEventSchema)
async def record_event(req: TelemetryEventRequest) -> TelemetryEventSchema:
    event = _telemetry.record_event(req.name, req.data)
    return TelemetryEventSchema(
        event_id=event.event_id,
        name=event.name,
        data=event.data,
        timestamp=event.timestamp,
    )


@router.post("/telemetry/flush", response_model=list[TelemetryEventSchema])
async def flush_telemetry() -> list[TelemetryEventSchema]:
    events = _telemetry.flush()
    return [
        TelemetryEventSchema(
            event_id=e.event_id, name=e.name, data=e.data, timestamp=e.timestamp
        )
        for e in events
    ]


@router.get("/telemetry/summary", response_model=TelemetrySummarySchema)
async def telemetry_summary() -> TelemetrySummarySchema:
    s = _telemetry.summary()
    return TelemetrySummarySchema(
        total_events=s["total_events"],
        unflushed=s["unflushed"],
        event_counts=s["event_counts"],
    )


@router.post("/dataset/mine", response_model=DatasetSchema)
async def mine_dataset(req: DatasetMineRequest) -> DatasetSchema:
    ds = _dataset_miner.mine(req.source, req.filters)
    return DatasetSchema(
        source=ds.source,
        examples=[
            DatasetExampleSchema(
                input=e.input, output=e.output, tags=e.tags, metadata=e.metadata
            )
            for e in ds.examples
        ],
        total=ds.total,
        filters_applied=ds.filters_applied,
    )


@router.post("/reward/score", response_model=RewardScoreSchema)
async def score_reward(req: RewardScoreRequest) -> RewardScoreSchema:
    score = _reward.score(req.trajectory)
    return RewardScoreSchema(score=score)


@router.post("/synthetic/generate", response_model=list[SyntheticTaskSchema])
async def generate_synthetic(req: SyntheticRequest) -> list[SyntheticTaskSchema]:
    tasks = _synthetic.generate(req.domain, req.n)
    return [
        SyntheticTaskSchema(
            task_id=t.task_id,
            domain=t.domain,
            description=t.description,
            expected_output_hint=t.expected_output_hint,
            difficulty=t.difficulty,
            tags=t.tags,
        )
        for t in tasks
    ]


@router.post("/refresh/schedule", response_model=RefreshJobSchema)
async def schedule_refresh(req: RefreshScheduleRequest) -> RefreshJobSchema:
    job = _refresh.schedule_refresh(req.model_id, req.dataset_id, req.params)
    return RefreshJobSchema(
        refresh_id=job.refresh_id,
        model_id=job.model_id,
        dataset_id=job.dataset_id,
        status=job.status.value,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


@router.get("/refresh/{refresh_id}", response_model=RefreshJobSchema)
async def refresh_status(refresh_id: str) -> RefreshJobSchema:
    job = _refresh.status(refresh_id)
    if not job:
        raise HTTPException(404, f"Refresh job {refresh_id} not found")
    return RefreshJobSchema(
        refresh_id=job.refresh_id,
        model_id=job.model_id,
        dataset_id=job.dataset_id,
        status=job.status.value,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


@router.delete("/refresh/{refresh_id}", response_model=dict)
async def cancel_refresh(refresh_id: str) -> dict[str, Any]:
    cancelled = _refresh.cancel(refresh_id)
    return {"refresh_id": refresh_id, "cancelled": cancelled}
