"""Self-Improvement Orchestrator – analyses failures and suggests improvements."""

from __future__ import annotations

import logging
from typing import Any

from minigun.models.core import EvalResult

logger = logging.getLogger(__name__)


class SelfImprovementOrchestrator:
    """Identifies failure patterns and proposes platform improvements."""

    def analyze_failures(self, eval_results: list[EvalResult]) -> list[dict[str, Any]]:
        """Identify recurring failure patterns from eval results."""
        failures = [r for r in eval_results if not r.passed]
        if not failures:
            logger.info("No failures to analyse")
            return []

        patterns: list[dict[str, Any]] = []

        # Low correctness pattern
        low_correctness = [r for r in failures if r.metrics.get("correctness", 1.0) < 0.5]
        if low_correctness:
            patterns.append({
                "pattern": "low_correctness",
                "count": len(low_correctness),
                "description": "Tasks are producing outputs that do not match expected values",
                "affected_task_ids": [r.task_id for r in low_correctness],
            })

        # Low completeness pattern
        low_completeness = [r for r in failures if r.metrics.get("completeness", 1.0) < 0.5]
        if low_completeness:
            patterns.append({
                "pattern": "low_completeness",
                "count": len(low_completeness),
                "description": "Tasks are missing expected output keys",
                "affected_task_ids": [r.task_id for r in low_completeness],
            })

        # Score distribution
        avg_score = sum(r.score for r in failures) / len(failures)
        patterns.append({
            "pattern": "overall_failure_rate",
            "failure_count": len(failures),
            "total_count": len(eval_results),
            "average_score": round(avg_score, 2),
            "description": f"{len(failures)}/{len(eval_results)} evals failed with avg score {avg_score:.2f}",
        })

        return patterns

    def suggest_improvements(self, eval_results: list[EvalResult] | None = None) -> list[dict[str, Any]]:
        """Return improvement suggestions based on analysis."""
        suggestions: list[dict[str, Any]] = [
            {
                "id": "improve_solver_output_schema",
                "priority": "high",
                "description": "Standardise solver output schemas to always include 'status', 'task', and domain-specific keys.",
                "rationale": "Critic agent penalises missing output keys; uniform schemas improve verification scores.",
            },
            {
                "id": "add_retry_backoff",
                "priority": "medium",
                "description": "Implement exponential back-off in WorkflowEngine retry logic.",
                "rationale": "Transient failures (network, rate-limits) are more likely to recover with back-off.",
            },
            {
                "id": "expand_mcp_stubs_to_real",
                "priority": "high",
                "description": "Replace MCP stubs with real API integrations (GitHub, Kubernetes, Terraform Cloud).",
                "rationale": "Stub MCPs limit the platform to simulation; real integrations unlock production value.",
            },
            {
                "id": "add_semantic_memory_vector_search",
                "priority": "medium",
                "description": "Replace linear episodic search with a vector embedding index (e.g. FAISS).",
                "rationale": "Semantic similarity search yields higher-quality context recall for the Planner.",
            },
        ]

        if eval_results:
            patterns = self.analyze_failures(eval_results)
            for p in patterns:
                if p.get("pattern") == "low_correctness":
                    suggestions.insert(0, {
                        "id": "tune_solver_for_correctness",
                        "priority": "critical",
                        "description": "Fine-tune solver prompts / heuristics to improve output correctness.",
                        "rationale": f"Detected {p['count']} tasks with correctness < 0.5.",
                    })

        return suggestions
