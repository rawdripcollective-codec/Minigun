"""ModelRefreshController: schedules and manages model refresh jobs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RefreshStatus(str, Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class RefreshJob:
    refresh_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str = ""
    dataset_id: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    status: RefreshStatus = RefreshStatus.SCHEDULED
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: str | None = None


class ModelRefreshController:
    def __init__(self) -> None:
        self._jobs: dict[str, RefreshJob] = {}

    def schedule_refresh(
        self, model_id: str, dataset_id: str, params: dict[str, Any] | None = None
    ) -> RefreshJob:
        job = RefreshJob(model_id=model_id, dataset_id=dataset_id, params=params or {})
        self._jobs[job.refresh_id] = job
        return job

    def status(self, refresh_id: str) -> RefreshJob | None:
        return self._jobs.get(refresh_id)

    def cancel(self, refresh_id: str) -> bool:
        job = self._jobs.get(refresh_id)
        if job and job.status == RefreshStatus.SCHEDULED:
            job.status = RefreshStatus.CANCELLED
            job.finished_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def list_jobs(self) -> list[RefreshJob]:
        return list(self._jobs.values())
