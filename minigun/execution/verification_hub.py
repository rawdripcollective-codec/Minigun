"""Verification Hub – aggregates critic and safety checks for a task result."""

from __future__ import annotations

import logging
from typing import Any

from minigun.agents.critic import CriticAgent
from minigun.agents.safety import SafetyEngine
from minigun.models.core import Task, VerificationResult

logger = logging.getLogger(__name__)


class VerificationHub:
    """Runs critic evaluation and safety checks and returns a combined result."""

    def __init__(
        self,
        critic: CriticAgent | None = None,
        safety: SafetyEngine | None = None,
    ) -> None:
        self._critic = critic or CriticAgent()
        self._safety = safety or SafetyEngine()

    def verify(self, task: Task, result: dict[str, Any]) -> VerificationResult:
        logger.info("VerificationHub verifying task id=%s name=%s", task.id, task.name)

        critic_result = self._critic.evaluate(task, result)
        safety_ok = self._safety.check(task, result)

        issues = list(critic_result.issues)
        if not safety_ok:
            issues.append("Safety policy check failed")

        passed = critic_result.passed and safety_ok
        score = critic_result.score if safety_ok else critic_result.score * 0.5

        return VerificationResult(
            passed=passed,
            score=round(score, 2),
            issues=issues,
        )
