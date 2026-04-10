"""WorkflowAutomationApp: creates and runs automations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AutomationDef:
    automation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger: dict[str, Any] = field(default_factory=dict)
    steps: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class AutomationRun:
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    automation_id: str = ""
    status: RunStatus = RunStatus.COMPLETED
    steps_executed: int = 0
    outputs: list[Any] = field(default_factory=list)
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: str | None = None


class WorkflowAutomationApp:
    def __init__(self) -> None:
        self._automations: dict[str, AutomationDef] = {}
        self._runs: dict[str, AutomationRun] = {}

    def create_automation(
        self, trigger: dict[str, Any], steps: list[dict[str, Any]]
    ) -> AutomationDef:
        auto = AutomationDef(trigger=trigger, steps=steps)
        self._automations[auto.automation_id] = auto
        return auto

    def run_automation(self, automation_id: str) -> AutomationRun:
        auto = self._automations.get(automation_id)
        run = AutomationRun(
            automation_id=automation_id,
            status=RunStatus.COMPLETED if auto else RunStatus.FAILED,
            steps_executed=len(auto.steps) if auto else 0,
            outputs=[{"step": s.get("name", f"step_{i}"), "status": "ok"} for i, s in enumerate(auto.steps)] if auto else [],
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        self._runs[run.run_id] = run
        return run

    def get_automation(self, automation_id: str) -> AutomationDef | None:
        return self._automations.get(automation_id)

    def get_run(self, run_id: str) -> AutomationRun | None:
        return self._runs.get(run_id)
