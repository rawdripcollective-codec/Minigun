"""OfflineEvaluator: evaluates task runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalResult:
    score: float  # 0-1
    breakdown: dict[str, float]
    notes: list[str]


class OfflineEvaluator:
    def evaluate(self, task_run: dict[str, Any]) -> EvalResult:
        notes: list[str] = []
        breakdown: dict[str, float] = {}

        # Correctness: did it complete?
        success = task_run.get("success", False)
        breakdown["correctness"] = 1.0 if success else 0.0
        if not success:
            notes.append("Task did not complete successfully.")

        # Efficiency: steps vs estimated
        steps_completed = task_run.get("steps_completed", 0)
        steps_total = task_run.get("steps_total", max(steps_completed, 1))
        breakdown["efficiency"] = round(steps_completed / steps_total, 3) if steps_total else 0.0

        # Quality: heuristic from metadata
        metadata = task_run.get("metadata", {})
        quality_hint = float(metadata.get("quality_hint", 0.7))
        breakdown["quality"] = max(0.0, min(1.0, quality_hint))

        # Weighted score
        score = (
            breakdown["correctness"] * 0.5
            + breakdown["efficiency"] * 0.3
            + breakdown["quality"] * 0.2
        )

        if score >= 0.8:
            notes.append("High-quality task run.")
        elif score >= 0.5:
            notes.append("Acceptable task run with room for improvement.")
        else:
            notes.append("Low-quality task run; review and retry.")

        return EvalResult(score=round(score, 3), breakdown=breakdown, notes=notes)
