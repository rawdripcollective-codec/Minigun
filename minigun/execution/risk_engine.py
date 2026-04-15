"""Risk Engine – scores the riskiness of task execution results."""

from __future__ import annotations

import logging
from typing import Any

from minigun.models.core import RiskLevel, RiskScore, Task

logger = logging.getLogger(__name__)

# Base risk scores per task type
_BASE_RISK: dict[str, float] = {
    "code": 0.2,
    "infra": 0.5,
    "sre": 0.6,
    "data": 0.3,
}

# Additional risk factors applied as multipliers on the base score
_RISK_KEYWORDS: dict[str, float] = {
    "destroy": 0.4,
    "delete": 0.3,
    "drop": 0.3,
    "prod": 0.2,
    "production": 0.2,
    "rollback": 0.1,
    "apply": 0.1,
    "deploy": 0.1,
}

APPROVAL_THRESHOLD = 0.7


def _level_for_score(score: float) -> str:
    if score >= 0.8:
        return RiskLevel.CRITICAL
    if score >= 0.6:
        return RiskLevel.HIGH
    if score >= 0.35:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


class RiskEngine:
    """Computes a RiskScore for a completed task."""

    def score(self, task: Task, result: dict[str, Any]) -> RiskScore:
        logger.info("RiskEngine scoring task id=%s name=%s", task.id, task.name)

        base = _BASE_RISK.get(task.type, 0.3)
        factors: list[str] = [f"base_risk_for_{task.type}_task"]
        penalty = 0.0

        name_lower = task.name.lower()
        for keyword, extra in _RISK_KEYWORDS.items():
            if keyword in name_lower:
                factors.append(f"keyword_match:{keyword}")
                penalty += extra

        # Penalise failed or errored results
        if result.get("error"):
            factors.append("task_has_error_output")
            penalty += 0.3

        # Penalise wide scope (many outputs)
        if len(result) > 10:
            factors.append("wide_output_scope")
            penalty += 0.1

        final_score = min(1.0, round(base + penalty, 2))
        level = _level_for_score(final_score)
        requires_approval = final_score >= APPROVAL_THRESHOLD

        return RiskScore(
            score=final_score,
            level=level,
            factors=factors,
            requires_approval=requires_approval,
        )
