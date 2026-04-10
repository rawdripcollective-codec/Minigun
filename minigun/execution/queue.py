"""JobQueue: async FIFO job queue."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    payload: dict[str, Any] = field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED
    result: Any = None
    error: str | None = None


class JobQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._jobs: dict[str, Job] = {}

    async def enqueue(self, payload: dict[str, Any]) -> str:
        job = Job(payload=payload)
        self._jobs[job.job_id] = job
        await self._queue.put(job.job_id)
        return job.job_id

    async def dequeue(self) -> Job | None:
        try:
            job_id = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None
        return self._jobs.get(job_id)

    def status(self, job_id: str) -> JobStatus | None:
        job = self._jobs.get(job_id)
        return job.status if job else None

    def list_jobs(self) -> list[Job]:
        return list(self._jobs.values())

    def get_job(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)
