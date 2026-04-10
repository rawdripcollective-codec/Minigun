"""Safety / Policy Engine – enforces guardrails on task execution."""

from __future__ import annotations

import logging
from typing import Any

from minigun.models.core import RiskScore, Task

logger = logging.getLogger(__name__)

# Task names that are always considered high-risk
_HIGH_RISK_PATTERNS: list[str] = [
    "destroy",
    "delete",
    "drop",
    "prod",
    "production",
    "rollback",
    "apply",
]

# Risk threshold above which manual approval is required
APPROVAL_THRESHOLD = 0.7


class SafetyEngine:
    """Checks tasks against safety policies and decides if approval is needed."""

    def check(self, task: Task, result: dict[str, Any]) -> bool:
        """Return True if the task/result passes all safety checks."""
        logger.info("SafetyEngine checking task id=%s name=%s", task.id, task.name)

        # Reject tasks that errored out
        if result.get("error"):
            logger.warning("Safety check failed: task has error output")
            return False

        # Reject tasks whose output contains an explicit 'blocked' marker
        if result.get("blocked"):
            logger.warning("Safety check failed: output is marked blocked")
            return False

        return True

    def requires_approval(self, risk_score: RiskScore) -> bool:
        """Return True if the risk score is above the approval threshold."""
        return risk_score.score >= APPROVAL_THRESHOLD or risk_score.requires_approval
