"""Critic/Verifier Agent – evaluates task outputs for correctness."""

from __future__ import annotations

import logging
from typing import Any

from minigun.models.core import Task, VerificationResult

logger = logging.getLogger(__name__)

# Minimum output keys expected per task type
_REQUIRED_OUTPUT_KEYS: dict[str, list[str]] = {
    "code": ["status"],
    "infra": ["status"],
    "sre": ["status"],
    "data": ["status"],
}


class CriticAgent:
    """Evaluates the output of a completed task and returns a VerificationResult."""

    def evaluate(self, task: Task, result: dict[str, Any]) -> VerificationResult:
        logger.info("Critic evaluating task id=%s name=%s", task.id, task.name)

        issues: list[str] = []
        score = 1.0

        # Check that result is not empty
        if not result:
            issues.append("Task produced empty output")
            score -= 0.5

        # Check for explicit error marker
        if result.get("error"):
            issues.append(f"Task reported error: {result['error']}")
            score -= 0.4

        # Check expected keys are present
        required = _REQUIRED_OUTPUT_KEYS.get(task.type, [])
        for key in required:
            if key not in result:
                issues.append(f"Missing expected output key: '{key}'")
                score -= 0.1

        # Check status field if present
        if "status" in result and result["status"] not in ("ok", "success", "completed"):
            issues.append(f"Unexpected status value: {result['status']}")
            score -= 0.2

        score = max(0.0, round(score, 2))
        passed = score >= 0.6 and not any("error" in i.lower() for i in issues)

        return VerificationResult(passed=passed, score=score, issues=issues)
