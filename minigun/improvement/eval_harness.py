"""Eval Harness – runs evaluation suites against task outputs."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from minigun.models.core import EvalResult

logger = logging.getLogger(__name__)

# Metric names that must be present for a "passing" eval
_REQUIRED_METRICS = {"correctness", "completeness"}

_SCORE_THRESHOLD = 0.7


class EvalHarness:
    """Evaluates task outputs against expected results."""

    def run_eval(
        self,
        task_id: str,
        expected: dict[str, Any],
        actual: dict[str, Any],
    ) -> EvalResult:
        logger.info("EvalHarness running eval for task_id=%s", task_id)

        metrics: dict[str, float] = {}
        issues: list[str] = []

        # Correctness: fraction of expected keys with matching values
        if expected:
            matches = sum(1 for k, v in expected.items() if actual.get(k) == v)
            metrics["correctness"] = round(matches / len(expected), 2)
        else:
            metrics["correctness"] = 1.0

        # Completeness: fraction of expected keys present in actual
        if expected:
            present = sum(1 for k in expected if k in actual)
            metrics["completeness"] = round(present / len(expected), 2)
        else:
            metrics["completeness"] = 1.0

        # Status check
        if actual.get("status") not in ("ok", "success", "completed", None):
            metrics["status_ok"] = 0.0
            issues.append(f"Unexpected status: {actual.get('status')}")
        else:
            metrics["status_ok"] = 1.0

        score = round(sum(metrics.values()) / len(metrics), 2)
        passed = score >= _SCORE_THRESHOLD

        return EvalResult(
            run_id=str(uuid.uuid4()),
            task_id=task_id,
            score=score,
            metrics=metrics,
            passed=passed,
        )

    def run_suite(self, suite: list[dict[str, Any]]) -> list[EvalResult]:
        """Run a list of eval specs, each with task_id, expected, actual keys."""
        results: list[EvalResult] = []
        for spec in suite:
            result = self.run_eval(
                task_id=spec.get("task_id", str(uuid.uuid4())),
                expected=spec.get("expected", {}),
                actual=spec.get("actual", {}),
            )
            results.append(result)
        return results
